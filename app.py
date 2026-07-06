# bancheck API - by pankaj-ux
from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

S2G_COOKIES = {
    '_ga': 'GA1.1.2123120599.1674510784',
    '_fbp': 'fb.1.1674510785537.363500115',
    '_ga_7JZFJ14B0B': 'GS1.1.1674510784.1.1.1674510789.0.0.0',
    'source': 'mb',
    'region': 'MA',
    'language': 'ar',
    '_ga_TVZ1LG7BEB': 'GS1.1.1674930050.3.1.1674930171.0.0.0',
    'datadome': '6h5F5cx_GpbuNtAkftMpDjsbLcL3op_5W5Z-npxeT_qcEe_7pvil2EuJ6l~JlYDxEALeyvKTz3~LyC1opQgdP~7~UDJ0jYcP5p20IQlT3aBEIKDYLH~cqdfXnnR6FAL0',
    'session_key': 'efwfzwesi9ui8drux4pmqix4cosane0y',
}

S2G_HEADERS = {
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'Origin': 'https://shop2game.com',
    'Referer': 'https://shop2game.com/app/100067/idlogin',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 11; Redmi Note 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36',
    'accept': 'application/json',
    'content-type': 'application/json',
    'sec-ch-ua': '"Chromium";v="107", "Not=A?Brand";v="24"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'x-datadome-clientid': '6h5F5cx_GpbuNtAkftMpDjsbLcL3op_5W5Z-npxeT_qcEe_7pvil2EuJ6l~JlYDxEALeyvKTz3~LyC1opQgdP~7~UDJ0jYcP5p20IQlT3aBEIKDYLH~cqdfXnnR6FAL0',
}

BAN_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'authority': 'ff.garena.com',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'referer': 'https://ff.garena.com/en/support/',
    'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'x-requested-with': 'B6FksShzIgjfrYImLpTsadjS86sddhFH',
}


def check_player_info(target_id):
    # Step 1: nickname + region fetch
    try:
        res = requests.post(
            'https://shop2game.com/api/auth/player_id_login',
            cookies=S2G_COOKIES,
            headers=S2G_HEADERS,
            json={'app_id': 100067, 'login_id': target_id, 'app_server_id': 0},
            timeout=10
        )
        if res.status_code != 200 or not res.json().get('nickname'):
            return {"error": "ID NOT FOUND"}

        player_data = res.json()
        nickname = player_data.get('nickname', 'N/A')
        region = player_data.get('region', 'N/A')

    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}

    # Step 2: Ban check
    try:
        ban_resp = requests.get(
            f'https://ff.garena.com/api/antihack/check_banned?lang=en&uid={target_id}',
            headers=BAN_HEADERS,
            timeout=10
        )
        ban_data = ban_resp.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Ban check failed: {str(e)}"}

    if ban_data.get("status") != "success" or "data" not in ban_data:
        return {"error": "Failed to retrieve ban status"}

    is_banned = ban_data["data"].get("is_banned", 0)
    period = ban_data["data"].get("period", 0)

    # Step 3: Ban info set karo
    if is_banned:
        if period == 0:
            ban_status = "banned"
            ban_period = "permanent"
            ban_reason = "This account was confirmed for using cheats."
        else:
            ban_status = "banned"
            ban_period = f"{period} month(s)"
            ban_reason = "temporarily banned due to unusual activities found with this account"
    else:
        ban_status = "not banned"
        ban_period = None
        ban_reason = "account safe (not banned)"

    return {
        "uid": target_id,
        "nickname": nickname,
        "region": region,
        "ban_status": ban_status,
        "ban_period": ban_period,
        "ban_reason": ban_reason,
    }


@app.route('/bancheck', methods=['GET'])
def check_ban_status():
    uid = request.args.get('uid')
    if not uid:
        return jsonify({"error": "UID parameter is required"}), 400

    result = check_player_info(uid)
    if "error" in result:
        return jsonify(result), 404

    return jsonify(result)


@app.route('/')
def home():
    return jsonify({
        "api": "Free Fire Ban Check API",
        "developer": "pankaj-ux",
        "endpoint": "/bancheck?uid=UID"
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 2003))
    app.run(host='0.0.0.0', port=port)
