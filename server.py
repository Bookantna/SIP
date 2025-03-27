import socket
import threading
from ip_converter import *

SIP_PORT = 5060
RTP_PORT = 4000  # พอร์ตรับเสียง RTP

# สร้าง UDP socket สำหรับ SIP
sip_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sip_sock.bind(("10.66.92.221", SIP_PORT))

# สร้าง UDP socket สำหรับ RTP (เสียง)
rtp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
rtp_sock.bind(("10.66.92.221", RTP_PORT))

print(f"📡 SIP Server is running on port {SIP_PORT}")
print(f"🎙️ RTP Server is listening on port {RTP_PORT}")


def handle_rtp():
    while True:
        try:
            rtp_data, rtp_addr = rtp_sock.recvfrom(2048)
            print(f"🔊 Received RTP audio from {(rtp_addr)}")
            

            # ส่ง RTP data ไปยัง client
            to_receiver = (str(chunk_to_ip(rtp_data[4:8])),4000)
            print(to_receiver, rtp_addr)
            rtp_sock.sendto(rtp_data, to_receiver)
        except Exception as e:
            print(f"❌ Error: {e}")


def handle_sip():
    while True:
        try:
            data, addr = sip_sock.recvfrom(1024)
            request = data.decode()
            print(f"📥 Received SIP request from {addr}:\n{request}")

            if request.startswith("INVITE"):
                # ตอบกลับ 100 Trying
                sip_sock.sendto(b"SIP/2.0 100 Trying\r\n\r\n", addr)

                # ตอบกลับ 180 Ringing
                sip_sock.sendto(b"SIP/2.0 180 Ringing\r\n\r\n", addr)

                # ตอบกลับ 200 OK (รับสาย)
                sip_response = f"""SIP/2.0 200 OK
Via: SIP/2.0/UDP {addr[0]}:5060
From: <sip:caller@{addr[0]}>
To: <sip:receiver@{addr[0]}>;tag=12345
Call-ID: 12345678@{addr[0]}
CSeq: 1 INVITE
Contact: <sip:receiver@{addr[0]}>
Content-Type: application/sdp
Content-Length: 100

v=0
o=- 0 0 IN IP4 {addr[0]}
s=VoIP Call
c=IN IP4 {addr[0]}
t=0 0
m=audio {RTP_PORT} RTP/AVP 0
a=rtpmap:0 PCMU/8000
"""

                sip_sock.sendto(sip_response.encode(), addr)
                print("✅ Sent SIP 200 OK response")
                print("🎧 Waiting for RTP audio...")

        except Exception as e:
            print(f"❌ Error: {e}")


# เริ่ม thread สำหรับการจัดการ SIP และ RTP
sip_thread = threading.Thread(target=handle_sip)
sip_thread.daemon = True
sip_thread.start()

rtp_thread = threading.Thread(target=handle_rtp)
rtp_thread.daemon = True
rtp_thread.start()

# รอให้โปรแกรมทำงานไปเรื่อยๆ
while True:
    pass
