import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def encrypt(plain_text, key):
    """
    Verschlüsselt den Text und verpackt Nonce und Ciphertext
    in eine Liste, die als String in die Datei geschrieben wird.
    """
    aesgcm = AESGCM(key)
    # Generiere eine sichere, zufällige 12-Byte Nonce
    nonce = os.urandom(12)

    # Verschlüsseln
    ciphertext = aesgcm.encrypt(nonce, plain_text.encode(), None)

    # Wir geben das Paar als String-Repräsentation einer Liste zurück.
    # Das landet so in der passwörter.txt (z.B. "['nonce_hex', 'cipher_hex']")
    return str([nonce.hex(), ciphertext.hex()])


def decrypt(encrypted_list, key):
    """
    Erhält die von ast.literal_eval umgewandelte Liste
    und entschlüsselt die Daten mit dem übergebenen Schlüssel.
    """
    aesgcm = AESGCM(key)

    # Hier liest er die Liste aus: [0] ist die Nonce, [1] der Ciphertext
    nonce = bytes.fromhex(encrypted_list[0])
    ciphertext = bytes.fromhex(encrypted_list[1])

    # Entschlüsseln
    decrypted_bytes = aesgcm.decrypt(nonce, ciphertext, None)
    return decrypted_bytes.decode()
if __name__ == "__main__":
    encrypted = encrypt("wgDAc4rUqaCvSwE", key)
    print("Verschlüsselt:", encrypted)

    # 3. Entschlüsseln
    decrypted = decrypt(encrypted, key)
    print("Entschlüsselt:", decrypted)
    print(key)