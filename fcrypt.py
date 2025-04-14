from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
import sys

def enc_dec(enc_dec, key_file, input_text):
    ENCRYPT = "encrypt"
    DECRYPT = "decrypt"

    if not len(sys.argv) == 5:
        print(f"Invalid arguments. Please enter: [{ENCRYPT}/{DECRYPT}] [key file] [input text]")
        sys.exit(1)

    action = enc_dec
    if not action in [ENCRYPT, DECRYPT]:
        print(f"Invalid argument: please select either '{ENCRYPT}' or '{DECRYPT}'")
        sys.exit(1)

    key_file = key_file
    input_text =sys.argv[3]

    if action == ENCRYPT:
        public_key = RSA.import_key(open(key_file).read())
        session_key = get_random_bytes(16)

        # Encrypt session key
        cipher_rsa = PKCS1_OAEP.new(public_key)
        enc_session_key = cipher_rsa.encrypt(session_key)

        # Encrypt data w/ the AES session key
        cipher_aes = AES.new(session_key, AES.MODE_EAX)
        ciphertext, tag = cipher_aes.encrypt_and_digest(input_text)

        # Save encrypted data to file

        # Feedback for user, then program closes
        print("Encryption Successful.")
        return [enc_session_key, cipher_aes.nonce, tag, ciphertext]


    if action == DECRYPT:
        # Get decode key
        private_key = RSA.import_key(open(key_file).read())
        # Open encrypted file
        enc_session_key = input_text[0]
        nonce = input_text[1]
        tag = input_text[2]
        ciphertext = input_text[3]

        # Decrypt session key w/ provided key
        try:
            cipher_rsa = PKCS1_OAEP.new(private_key)
            session_key = cipher_rsa.decrypt(enc_session_key)

            # Decrypt data w/ session key
            cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
            data = cipher_aes.decrypt_and_verify(ciphertext, tag)
        except ValueError:
            print("The message was modified!")
            sys.exit(2)

        # Feedback for user, then program closes
        print("Decryption Successful.")
        return data

#########
# Start #
#########
if __name__ == "__main__":
    enc_dec(sys.argv[1], sys.argv[2], sys.argv[3])