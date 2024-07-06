class ASD:
    tuples = {}

class ABC:
    @staticmethod
    def add():
        ASD.tuples["Minidump"] = {"Location": "C:\\Users\\UTQ\\PycharmProjects\\Evidence-analysis\\get_data.py", "Name": "miniDump.py"}
        ASD.tuples["CrashDump"] = {"Location": "C:\\Users\\UTQ\\PycharmProjects\\Evidence-analysis\\get_data.py", "Name": "crashDump.py"}

        return ASD.tuples

ABC.add()

for key, value in ASD.tuples.items():
    print(key)
    for k, v in value.items():
        print("\t", k, ":", v)