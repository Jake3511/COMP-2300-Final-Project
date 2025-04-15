from Crypto.PublicKey import RSA

def gen_keys(username:str)->None:
    key = RSA.generate(2048)
    private_key = key.export_key()
    with open(f"./private/{username}_key.pem", "wb") as f:
        f.write(private_key)

    public_key = key.publickey().export_key()
    with open(f"./public/{username}_key.pem", "wb") as f:
        f.write(public_key)

