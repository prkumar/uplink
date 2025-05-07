import uplink


class HttpBin(uplink.Consumer):
    @uplink.multipart
    @uplink.post("post")
    def post(self, attachments: uplink.PartMap):
        pass


client = HttpBin(base_url="https://httpbin.org/")


print(
    client.post(
        attachments={
            "file1.txt": [open("file1.txt", "rb"), open("file1.txt", "rb")]
        }
    )
)
