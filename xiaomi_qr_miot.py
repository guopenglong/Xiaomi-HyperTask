#!/usr/bin/env python3
"""Standalone Xiaomi QR login + MIoT CLI."""

from __future__ import annotations

import argparse
import base64
import json
import time
import uuid
from hashlib import sha1, sha256
from hmac import new as hmac_new
from os import urandom
from pathlib import Path
from random import choice
from typing import Any, Callable
from urllib.parse import quote

import requests

ACCOUNT_BASE = "https://account.xiaomi.com"
QR_LOGIN_URL = f"{ACCOUNT_BASE}/longPolling/loginUrl"
QR_SID = "iccc_app_api"
MIOT_SID = "xiaomiio"
QR_CALLBACK = "https://mobile.iccc.xiaomiev.com/mobile/sts"
TOKEN_FILE = Path(__file__).with_suffix(".token.json")
JSON_PREFIX = "&&&START&&&"
UA_LOGIN = "APP/com.xiaomi.mihome APPV/11.3.203 iosPassportSDK/4.2.50 iOS/26.3.1 MK/aVBob25lMTcsMg== DEVT/aVBob25l DEVS/aU9T BRA/QXBwbGU= L/zh_CN"
UA_MIIO = "iOS-14.4-6.0.103-iPhone12,3--0000000000000000000000000000000000000000-0-0000000000000000-iPhone"
DEVICES = [
    ("2210132C", "Xiaomi 13 Pro", "13", "TQ2A.230505.002"),
    ("23127PN0CC", "Xiaomi 14", "14", "UQ1A.240105.004"),
    ("2312DRA49G", "Xiaomi 14 Pro", "14", "UQ1A.240105.004"),
    ("25128PNA1C", "Xiaomi 15 Ultra", "15", "BP2A.250605.031.A3"),
]


class AuthError(RuntimeError):
    pass


load = lambda p: json.loads(p.read_text(encoding="utf-8")) if p.exists() else None
save = lambda p, d: p.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")
dump = lambda d: print(json.dumps(d, ensure_ascii=False, indent=2) if isinstance(d, (dict, list)) else d)


def prefixed_json(text: str) -> dict[str, Any]:
    return json.loads(text[len(JSON_PREFIX):] if text.startswith(JSON_PREFIX) else text)


def login_session() -> requests.Session:
    code, name, android, build = choice(DEVICES)
    ua = (
        f"Dalvik/2.1.0 (Linux; U; Android {android}; {code} Build/{build}) "
        f"APP/car.mobile APPV/26040914 MK/{base64.b64encode(name.encode()).decode()} "
        f"SDKV/5.3.0 PassportSDK/5.3.0 XiaomiAccountSSO/5.3.0 "
        f"CPN/com.mi.car.mobile passport-ui/5.3.0 "
        f"DEVT/UGhvbmU= BRA/WGlhb21p DEVS/QW5kcm9pZA=="
    )
    s = requests.Session()
    s.headers.update({
        "User-Agent": ua,
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip",
        "Connection": "Keep-Alive",
    })
    return s


def show_qr(login_url: str, image_url: str) -> None:
    try:
        import qrcode  # type: ignore

        qr = qrcode.QRCode(border=1)
        qr.add_data(login_url)
        qr.make(fit=True)
        qr.print_ascii(invert=True)
    except ImportError:
        pass
    print(f"二维码图片: {image_url}")
    if login_url and login_url != image_url:
        print(f"登录链接:   {login_url}")


def qr_login() -> dict[str, Any]:
    s = login_session()
    device_id = "an_" + uuid.uuid4().hex
    s.cookies.set("deviceId", device_id, domain="account.xiaomi.com")
    qr = prefixed_json(s.get(QR_LOGIN_URL, params={
        "_qrsize": "480",
        "qs": f"%3Fsid%3D{QR_SID}%26_json%3Dtrue",
        "callback": QR_CALLBACK,
        "_hasLogo": "false",
        "sid": QR_SID,
        "serviceParam": "",
        "_locale": "zh_CN",
        "_dc": str(int(time.time() * 1000)),
    }, timeout=30).text)
    poll_url = qr.get("lp")
    if not poll_url:
        raise RuntimeError(f"获取二维码失败: {qr}")
    show_qr(qr.get("loginUrl", "") or qr.get("qr", ""), qr.get("qr", ""))
    print(f"等待扫码... (有效期 {float(qr.get('timeout', 300)):.0f} 秒)")

    deadline = time.time() + float(qr.get("timeout", 300))
    while True:
        if time.time() > deadline:
            raise RuntimeError("二维码扫码超时")
        try:
            resp = s.get(poll_url, timeout=65)
            if resp.status_code == 200:
                data = prefixed_json(resp.text)
                break
        except requests.Timeout:
            continue
        except requests.RequestException as exc:
            print(f"轮询失败: {exc}，继续等待...")
        time.sleep(2)

    location = data.get("location")
    pass_token = data.get("passToken") or s.cookies.get("passToken")
    if not location or not data.get("userId") or not pass_token:
        raise RuntimeError(f"扫码登录返回异常: {data}")
    s.get(location, timeout=30).raise_for_status()
    return {
        "userId": str(data["userId"]),
        "passToken": pass_token,
        "deviceId": device_id,
        "lastQrLoginAt": int(time.time()),
    }


def mint_miot_token(auth: dict[str, Any]) -> dict[str, Any]:
    s = requests.Session()
    s.headers.update({"User-Agent": UA_LOGIN})
    for key, value in {
        "sdkVersion": "3.9",
        "deviceId": auth["deviceId"],
        "userId": auth["userId"],
        "passToken": auth["passToken"],
    }.items():
        s.cookies.set(key, value, domain="account.xiaomi.com")

    data = prefixed_json(s.get(
        f"{ACCOUNT_BASE}/pass/serviceLogin",
        params={"sid": MIOT_SID, "_json": "true"},
        timeout=30,
    ).text)
    if data.get("code") != 0 or any(k not in data for k in ("location", "nonce", "ssecurity")):
        raise RuntimeError(f"换取 xiaomiio 凭据失败: {data}")

    location = str(data["location"])
    if not location.startswith("http"):
        location = ACCOUNT_BASE + location
    client_sign = base64.b64encode(sha1(f"nonce={data['nonce']}&{data['ssecurity']}".encode()).digest()).decode()
    s.get(f"{location}&clientSign={quote(client_sign)}", timeout=30).raise_for_status()
    service_token = s.cookies.get("serviceToken")
    if not service_token:
        raise RuntimeError("已拿到 ssecurity，但未拿到 xiaomiio serviceToken")
    auth.update({
        "xiaomiio_ssecurity": data["ssecurity"],
        "xiaomiio_serviceToken": service_token,
        "lastMiotLoginAt": int(time.time()),
    })
    return auth


def ensure_auth(token_file: Path, force_qr: bool = False, refresh: bool = False) -> dict[str, Any]:
    auth = None if force_qr else load(token_file)
    if not auth or any(not auth.get(k) for k in ("userId", "passToken", "deviceId")):
        auth, refresh = qr_login(), True
    if refresh or not auth.get("xiaomiio_ssecurity") or not auth.get("xiaomiio_serviceToken"):
        auth = mint_miot_token(auth)
        save(token_file, auth)
    return auth


def sign_nonce(ssecurity: str, nonce: str) -> str:
    h = sha256()
    h.update(base64.b64decode(ssecurity))
    h.update(base64.b64decode(nonce))
    return base64.b64encode(h.digest()).decode()


def sign_data(uri: str, data: Any, ssecurity: str) -> dict[str, str]:
    data = data if isinstance(data, str) else json.dumps(data)
    nonce = base64.b64encode(urandom(8) + int(time.time() / 60).to_bytes(4, "big")).decode()
    snonce = sign_nonce(ssecurity, nonce)
    sign = hmac_new(
        key=base64.b64decode(snonce),
        msg="&".join([uri, snonce, nonce, "data=" + data]).encode(),
        digestmod=sha256,
    ).digest()
    return {"_nonce": nonce, "data": data, "signature": base64.b64encode(sign).decode()}


def api_base(region: str) -> str:
    return f"https://{'' if region in ('', 'cn') else region + '.'}api.io.mi.com/app"


def miio_request(auth: dict[str, Any], uri: str, data: Any, region: str = "cn") -> Any:
    resp = requests.post(
        api_base(region) + uri,
        data=sign_data(uri, data, auth["xiaomiio_ssecurity"]),
        headers={"User-Agent": UA_MIIO, "x-xiaomi-protocal-flag-cli": "PROTOCAL-HTTP2"},
        cookies={
            "userId": auth["userId"],
            "serviceToken": auth["xiaomiio_serviceToken"],
            "PassportDeviceId": auth["deviceId"],
        },
        timeout=30,
    )
    if resp.status_code == 401:
        raise AuthError("MIoT 请求返回 401")
    resp.raise_for_status()
    payload = resp.json()
    if payload.get("code") != 0:
        if "auth" in str(payload.get("message", "")).lower():
            raise AuthError(f"MIoT 认证失效: {payload}")
        raise RuntimeError(f"MIoT 请求失败: {payload}")
    return payload.get("result")


def miot_request(auth: dict[str, Any], cmd: str, params: Any, region: str = "cn") -> Any:
    return miio_request(auth, f"/miotspec/{cmd}", {"params": params}, region)


def iid_value(args: argparse.Namespace) -> tuple[int, int]:
    if args.iid:
        pos = args.iid.find("-")
        return (int(args.iid), 1) if pos == -1 else (int(args.iid[:pos]), int(args.iid[pos + 1 :]))
    if args.siid is None or args.piid is None:
        raise RuntimeError("请提供 --iid 2-1，或同时提供 --siid 与 --piid")
    return args.siid, args.piid


def parse_value(raw: str) -> Any:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


def with_auth(args: argparse.Namespace, action: Callable[[dict[str, Any]], Any]) -> Any:
    auth = ensure_auth(args.token_file, force_qr=args.force_qr)
    for i in range(3):
        try:
            result = action(auth)
            save(args.token_file, auth)
            return result
        except AuthError:
            if i == 0:
                print("检测到 MIoT 凭据失效，尝试使用 passToken 刷新...", flush=True)
                auth = ensure_auth(args.token_file, refresh=True)
            elif i == 1:
                print("passToken 也可能失效，重新扫码登录...", flush=True)
                auth = ensure_auth(args.token_file, force_qr=True, refresh=True)
            else:
                raise


def cmd_login(args: argparse.Namespace) -> None:
    auth = ensure_auth(args.token_file, force_qr=args.force_qr, refresh=True)
    save(args.token_file, auth)
    print(f"登录成功\nuserId: {auth['userId']}\ndeviceId: {auth['deviceId']}\ntoken: {args.token_file}")


def cmd_devices(args: argparse.Namespace) -> None:
    name = "full" if args.full else args.name

    def action(auth: dict[str, Any]) -> list[dict[str, Any]]:
        devices = ((miio_request(auth, "/home/device_list", {
            "getVirtualModel": bool(args.get_virtual_model),
            "getHuamiDevices": int(args.get_huami_devices),
        }, args.region) or {}).get("list") or [])
        if name == "full":
            return devices
        return [
            {"name": i.get("name"), "model": i.get("model"), "did": i.get("did"), "token": i.get("token")}
            for i in devices if not name or name in str(i.get("name", ""))
        ]

    dump(with_auth(args, action))


def cmd_get(args: argparse.Namespace) -> None:
    iid = iid_value(args)
    dump(with_auth(args, lambda auth: (
        (result := miot_request(auth, "prop/get", [{"did": args.did, "siid": iid[0], "piid": iid[1]}], args.region)),
        None if not isinstance(result, list) or not result else result[0].get("value") if result[0].get("code") == 0 else None,
    )[1]))


def cmd_set(args: argparse.Namespace) -> None:
    iid = iid_value(args)
    dump(with_auth(args, lambda auth: (
        (result := miot_request(auth, "prop/set", [{"did": args.did, "siid": iid[0], "piid": iid[1], "value": parse_value(args.value)}], args.region)),
        -1 if not isinstance(result, list) or not result else result[0].get("code", -1),
    )[1]))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="小米账号扫码登录 + MIoT 单文件工具")
    parser.add_argument("--token-file", type=Path, default=TOKEN_FILE, help=f"token 缓存文件，默认: {TOKEN_FILE}")
    parser.add_argument("--force-qr", action="store_true", help="忽略本地 token，强制重新扫码登录")
    subs = parser.add_subparsers(dest="command", required=True)

    subs.add_parser("login", help="扫码登录并保存 xiaomiio token").set_defaults(func=cmd_login)

    p = subs.add_parser("devices", help="查询设备列表")
    p.add_argument("--name", help="按设备名关键字过滤")
    p.add_argument("--full", action="store_true", help="输出完整原始设备信息")
    p.add_argument("--get-virtual-model", action="store_true", help="请求虚拟型号")
    p.add_argument("--get-huami-devices", type=int, default=0, help="是否包含华米设备，默认 0")
    p.add_argument("--region", default="cn", help="区域，默认 cn")
    p.set_defaults(func=cmd_devices)

    for name, help_text, func in (("get", "调用 miot_get_prop 读取属性", cmd_get), ("set", "调用 miot_set_prop 设置属性", cmd_set)):
        p = subs.add_parser(name, help=help_text)
        p.add_argument("--did", required=True, help="设备 did")
        p.add_argument("--iid", help="MIoT 属性，如 2-1")
        p.add_argument("--siid", type=int, help="服务 siid")
        p.add_argument("--piid", type=int, help="属性 piid")
        p.add_argument("--region", default="cn", help="区域，默认 cn")
        if name == "set":
            p.add_argument("--value", required=True, help="属性值，默认自动按 JSON 解析")
        p.set_defaults(func=func)
    return parser


def main() -> int:
    parser = build_parser()
    try:
        args = parser.parse_args()
        args.func(args)
        return 0
    except KeyboardInterrupt:
        print("已取消")
        return 130
    except Exception as exc:
        print(f"错误: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
