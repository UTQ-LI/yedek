import psutil, socket

class GetProccesses:
    @staticmethod
    def getProccesses():
        connections = psutil.net_connections()
        conn_info = []

        for conn in connections:
            try:
                name = psutil.Process(conn.pid).name()
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                name = "None"

            if conn.family == socket.AF_INET:
                family = "IPv4"
            elif conn.family == socket.AF_INET6:
                family = "IPv6"
            else:
                family = "UNKNOWN"

            if conn.type == socket.SOCK_STREAM:
                protocol = "TCP"
            elif conn.type == socket.SOCK_DGRAM:
                protocol = "UDP"
            else:
                protocol = "UNKNOWN"

            conn_info.append({"Process Name": name, "Local Address": conn.laddr if conn.laddr else "None", "Remote Address": conn.raddr if conn.raddr else "None", "Protocol": protocol, "Process ID": conn.pid, "Status": conn.status, "Family": family, "Type": conn.type})

        return conn_info
