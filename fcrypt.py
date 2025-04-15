from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
import sys

def enc_dec(username:str, enc_dec:str, priv_pub:str, input_file:str, output_file:str)->None:
    ENCRYPT = "encrypt"
    DECRYPT = "decrypt"
    PRIVATE = "private"
    PUBLIC = "public"

    if not len(sys.argv) == 6:
        print(f"Invalid arguments. Please enter: [username] [{ENCRYPT}/{DECRYPT}] [{PRIVATE}/{PUBLIC}] [input file] [output file]")
        return False

    action = enc_dec
    if not action in [ENCRYPT, DECRYPT]:
        print(f"Invalid argument: please select either '{ENCRYPT}' or '{DECRYPT}'")
        return False

    key_file = key_file

    if action == ENCRYPT:
        if priv_pub == PRIVATE:
            key_file = f"./{PRIVATE}/{username}_key.pem"
        elif priv_pub == PUBLIC:
            key_file = f"./{PUBLIC}/{username}_key.pem"
        else:
            print(f"Invalid Argument; priv_pub Must Be Either \"{PRIVATE}\" or \"{PUBLIC}\"")
            return False

        input_data =  open(input_file, "r").read().encode("utf-8")

        public_key = RSA.import_key(open(key_file).read())
        session_key = get_random_bytes(16)

        # Encrypt session key
        cipher_rsa = PKCS1_OAEP.new(public_key)
        enc_session_key = cipher_rsa.encrypt(session_key)

        # Encrypt data w/ the AES session key
        cipher_aes = AES.new(session_key, AES.MODE_EAX)
        ciphertext, tag = cipher_aes.encrypt_and_digest(input_data)

        # Save encrypted data to file
        with open(output_file, "wb") as f:
            f.write(enc_session_key)
            f.write(cipher_aes.nonce)
            f.write(tag)
            f.write(ciphertext)

        # Feedback for user, then program closes
        print("Encryption Successful.")
        return True


    if action == DECRYPT:
        # Get decode key
        if priv_pub == PRIVATE:
            key_file = f"./{PRIVATE}/{username}_key.pem"
        elif priv_pub == PUBLIC:
            key_file = f"./{PUBLIC}/{username}_key.pem"
        else:
            print(f"Invalid Argument; priv_pub Must Be Either \"{PRIVATE}\" or \"{PUBLIC}\"")
            return False


        private_key = RSA.import_key(open(key_file).read())
        # Open encrypted file
        with open(input_file, "rb") as f:
            enc_session_key = f.read(private_key.size_in_bytes())
            nonce = f.read(16)
            tag = f.read(16)
            ciphertext = f.read()

        # Decrypt session key w/ provided key
        try:
            cipher_rsa = PKCS1_OAEP.new(private_key)
            session_key = cipher_rsa.decrypt(enc_session_key)

            # Decrypt data w/ session key
            cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
            data = cipher_aes.decrypt_and_verify(ciphertext, tag)
        except ValueError:
            print("The message was modified!")
            return False

        # Feedback for user, then program closes
        print("Decryption Successful.")
        return True


#########
# Start #
#########
if __name__ == "__main__":
    enc_dec("test", sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])