import socket
import time
import pyaudio
from ip_converter import *
# SIP_SERVER = "10.66.92.221"  # IP of SIP Server
SIP_PORT = 5060
# CLIENT_IP = "10.66.92.221"  # IP of Client
# end_client = "10.66.92.124"
CLIENT_PORT = 5062  # SIP Client uses this port
RTP_PORT = 4002  # RTP port for sending audio

def call_ini(SIP_SERVER, CLIENT_IP, end_client):
    # Initialize PyAudio
    p = pyaudio.PyAudio()

    # Audio quality settings
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 8000  # 8 kHz for PCMU
    CHUNK = 200  # 10ms of audio data per chunk
    WIDTH = 2  # 2 bytes per sample (16-bit PCM)

    # Open input stream for microphone
    input_stream = p.open(
        format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK
    )

    # Open output stream for playing audio received from RTP
    output_stream = p.open(
        format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK
    )

    # Create UDP socket for SIP
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((CLIENT_IP, CLIENT_PORT))

    # SIP INVITE message body
    sip_invite_body = f"""v=0 
    o=- 0 0 IN IP4 {CLIENT_IP}
    s=VoIP Call
    c=IN IP4 {CLIENT_IP}
    t=0 0
    m=audio {RTP_PORT} RTP/AVP 0
    a=rtpmap:0 PCMU/8000
    """

    # SIP INVITE request
    sip_invite = f"""INVITE sip:user1@{end_client} SIP/2.0
    Via: SIP/2.0/UDP {CLIENT_IP}:{CLIENT_PORT};branch=z9hG4bK776asdhds
    Max-Forwards: 70
    To: <sip:user1@{end_client}>
    From: <sip:user2@{CLIENT_IP}>;tag=1928301774
    Call-ID: 12345678@{CLIENT_IP}
    CSeq: 1 INVITE
    Contact: <sip:user2@{CLIENT_IP}>
    Content-Type: application/sdp
    Content-Length: {len(sip_invite_body)}


    {sip_invite_body}
    """

    try:
        # Send SIP INVITE request
        sock.sendto(sip_invite.encode(), (SIP_SERVER, SIP_PORT))
        print("📨 SIP INVITE request sent.")

        # Receive response from SIP Server
        response, _ = sock.recvfrom(1024)
        print("📩 Response from server:")
        print(response.decode())

        # Open RTP socket for sending audio
        rtp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        rtp_sock.bind((CLIENT_IP, RTP_PORT ))  # Use a different port


        print("🎙️ Sending RTP audio packets...")

        while True:
            try:
                audio_data = input_stream.read(CHUNK)

                # # Create RTP packet (RTP header + audio data)
                receiver_chunk = socket.inet_aton(end_client)
                
                rtp_packet = b"\x80\x78\x00\x01"+ receiver_chunk + audio_data  # RTP header + audio data

                # # Send RTP packet to SIP Server
                rtp_sock.sendto(rtp_packet, (SIP_SERVER, RTP_PORT))
                rtp_sock.settimeout(0.01)
                rtp_data, addr = rtp_sock.recvfrom(2048)
                
                print(rtp_data, addr)

                if rtp_data:
                    if chunk_to_ip(rtp_data[4:8]) == CLIENT_IP:
                        audio_chunk = rtp_data[8:]  # Skip RTP header (first 8 bytes)
                        print(f"Playing audio from {addr[0]}:{addr[1]}")
                        output_stream.write(audio_chunk)
                    else:
                        print(f"⚠️ Received data from unexpected source: {addr[0]}:{addr[1]}")
                print(f"Received RTP data from {addr[0]}:{addr[1]}")
            except socket.timeout:
                print("⏳ No RTP data received (timeout)")

    except Exception as e:
        print(f"❌ Error: {e}")


    finally:
        # Clean up resources (close streams and sockets)
        try:
            if input_stream.is_active():
                input_stream.stop_stream()
            if output_stream.is_active():
                output_stream.stop_stream()
        except OSError:
            print("Stream is not open.")
        input_stream.close()
        output_stream.close()
        p.terminate()
        sock.close()
        rtp_sock.close()