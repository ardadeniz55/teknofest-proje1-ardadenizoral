"""TEKNOFEST Sürü İHA - Proje 1: ArduPilot SITL üzerinde kare uçuş.

Çalıştırma: SITL ve MAVProxy açıkken -> python3 kare_ucus.py
MAVProxy, --out udp:127.0.0.1:14550 ile bu betiğe veri yönlendirir.
"""
import csv
import time

from pymavlink import mavutil

BAGLANTI = "udp:127.0.0.1:14550"
IRTIFA = 10.0  # metre
KENAR = 20.0  # karenin kenar uzunluğu, metre


def mod_ayla(iha, mod):
    iha.set_mode(mod)
    while iha.flightmode != mod:
        iha.recv_match(type="HEARTBEAT", blocking=True)


def konuma_git(iha, kuzey, dogu, asagi):
    """Kalkış noktasına göre yerel NED koordinatına git (asagi negatif = yukarı)."""
    iha.mav.set_position_target_local_ned_send(
        0,
        iha.target_system,
        iha.target_component,
        mavutil.mavlink.MAV_FRAME_LOCAL_NED,
        0b110111111000,  # yalnızca konum alanlarını kullan
        kuzey,
        dogu,
        asagi,
        0,
        0,
        0,
        0,
        0,
        0,
        0,  # yaw
        0,  # yaw_rate
    )


def kayit_al(iha, yazici, baslangic):
    """GLOBAL_POSITION_INT mesajını okuyup CSV'ye bir satır yazar, irtifayı döndürür."""
    msg = iha.recv_match(
        type="GLOBAL_POSITION_INT", blocking=True, timeout=1
    )
    if msg is None:
        return None
    irtifa = msg.relative_alt / 1000.0
    yazici.writerow(
        [
            round(time.time() - baslangic, 2),
            msg.lat / 1e7,
            msg.lon / 1e7,
            irtifa,
        ]
    )
    return irtifa


def main():
    iha = mavutil.mavlink_connection(BAGLANTI)
    iha.wait_heartbeat()
    print("Bağlandı: sistem", iha.target_system)

    with open("ucus_kaydi.csv", "w", newline="") as f:
        yazici = csv.writer(f)
        yazici.writerow(["zaman_s", "enlem", "boylam", "irtifa_m"])

        baslangic = time.time()

        mod_ayla(iha, "GUIDED")
        iha.arducopter_arm()
        iha.motors_armed_wait()
        print("Motorlar açık")

        iha.mav.command_long_send(
            iha.target_system,
            iha.target_component,
            mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            IRTIFA,
        )

        print("Kalkış yapılıyor...")
        while True:
            anlik_irtifa = kayit_al(iha, yazici, baslangic)
            if anlik_irtifa is not None and anlik_irtifa >= IRTIFA * 0.95:
                print(f"Hedef irtifaya ulaşıldı: {anlik_irtifa:.2f} m")
                break
            time.sleep(0.2)

        koseler = [(KENAR, 0.0), (KENAR, KENAR), (0.0, KENAR), (0.0, 0.0)]

        for kuzey, dogu in koseler:
            konuma_git(iha, kuzey, dogu, -IRTIFA)

            while True:
                kayit_al(iha, yazici, baslangic)
                msg_pos = iha.recv_match(
                    type="LOCAL_POSITION_NED", blocking=True, timeout=1
                )
                if msg_pos is not None:
                    dx = msg_pos.x - kuzey
                    dy = msg_pos.y - dogu
                    mesafe = (dx ** 2 + dy ** 2) ** 0.5
                    if mesafe < 1.0:
                        break
                time.sleep(0.2)

            print("Köşeye ulaşıldı:", kuzey, dogu)

        mod_ayla(iha, "LAND")
        print("İniş moduna geçildi...")

        while True:
            anlik_irtifa = kayit_al(iha, yazici, baslangic)
            if anlik_irtifa is not None and anlik_irtifa < 0.3:
                break
            time.sleep(0.2)

        print("İniş tamam, kayıt: ucus_kaydi.csv")


if __name__ == "__main__":
    main()