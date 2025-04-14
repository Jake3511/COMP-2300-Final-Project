from Crypto.PublicKey import RSA

def gen_keys():
    key = RSA.generate(2048)
    private_key = key.export_key()
    with open("./private_key.pem", "wb") as f:
        f.write(private_key)

    public_key = key.publickey().export_key()
    with open("./public_key.pem", "wb") as f:
        f.write(public_key)

