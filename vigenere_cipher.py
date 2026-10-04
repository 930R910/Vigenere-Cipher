def show(text):
    return text.replace(" ", "_")


#vigenere substitution
def vigenere(text, key, decrypt=False):
    #turn each letter of the keyword into a number (A=0, B=1 ... Z=25)
    shifts = [ord(k) - ord('A') for k in key.upper() if k.isalpha()]
    #result is the new text, i only counts letters so the keyword skips spaces
    result, i = "", 0
    for ch in text:
        if ch.isalpha() and ch.isascii():
            #keep the case: uppercase starts at 'A', lowercase starts at 'a'
            base = ord('A') if ch.isupper() else ord('a')
            #take the next keyword shift, negative when decrypting
            shift = -shifts[i % len(shifts)] if decrypt else shifts[i % len(shifts)]
            #move the letter by the shift, % 26 keeps it inside the alphabet
            result += chr((ord(ch) - base + shift) % 26 + base)
            i += 1
        else:
            #spaces, numbers and punctuation stay the same
            result += ch
    return result


#Permutations
def get_order(key):
    #sorts the key positions by their character, ties go left to right
    return sorted(range(len(key)), key=lambda i: (key[i], i))


def column_perm(n, key):
    #Write text in rows under the key, read column by column in key order
    #returns a list of old positions in the new order
    return [i for col in get_order(key) for i in range(col, n, len(key))]


def row_perm(n, width, key):
    #Cut text into rows of `width`, reorder rows in groups of len(key) rows
    #start with every position staying where it is
    p = list(range(n))
    group = len(key)
    #only complete groups of rows get reordered, leftover rows stay in place
    for g in range((n // width) // group):
        #new_pos = where the row goes, old_pos = which row of the group goes there
        for new_pos, old_pos in enumerate(get_order(key)):
            #move every character of that row
            for c in range(width):
                p[(g * group + new_pos) * width + c] = (g * group + old_pos) * width + c
    return p


def permute(text, p):
    #build the new text by taking characters from the old text in the order of p
    return "".join(text[i] for i in p)


def unpermute(text, p):
    #put every character back in its old position
    old = [""] * len(text)
    for j, i in enumerate(p):
        old[i] = text[j]
    return "".join(old)


#rounds
def encrypt(text, rounds):
    print(f"Plaintext             : {show(text)}")
    #vigenere, then column permutation, then row permutation
    for n, (vkey, ckey, rkey) in enumerate(rounds, 1):
        text = vigenere(text, vkey)
        print(f"Round {n} Vigenere ({vkey}) : {show(text)}")
        text = permute(text, column_perm(len(text), ckey))
        print(f"Round {n} Columns  ({ckey}) : {show(text)}")
        #the row width is the length of the column key
        text = permute(text, row_perm(len(text), len(ckey), rkey))
        print(f"Round {n} Rows     ({rkey}) : {show(text)}")
    return text


def decrypt(text, rounds):
    print(f"Ciphertext            : {show(text)}")
    #go through the rounds backwards, from the last round to the first
    for n in range(len(rounds), 0, -1):
        vkey, ckey, rkey = rounds[n - 1]
        #undo the steps in the opposite order: rows, then columns, then vigenere
        text = unpermute(text, row_perm(len(text), len(ckey), rkey))
        print(f"Round {n} Undo Rows     ({rkey}) : {show(text)}")
        text = unpermute(text, column_perm(len(text), ckey))
        print(f"Round {n} Undo Columns  ({ckey}) : {show(text)}")
        text = vigenere(text, vkey, decrypt=True)
        print(f"Round {n} Undo Vigenere ({vkey}) : {show(text)}")
    return text


#Program
def ask(prompt, letters=False):
    while True:
        value = input(prompt).strip()
        if value and (not letters or any(c.isalpha() for c in value)):
            return value
        print("  Invalid, try again.")


def main():
    mode = ""
    while mode not in ("e", "d"):
        mode = input("Encrypt or Decrypt? (e/d): ").strip().lower()[:1]

    if mode == "e":
        text = input("Plaintext: ")
    else:
        #the ciphertext is given in hex, convert it back to normal text
        while True:
            try:
                text = bytes.fromhex("".join(input("Ciphertext (hex): ").split())).decode()
                break
            except ValueError:
                print("  Not a valid hex ciphertext, try again.")

    #number of rounds has to be a whole number
    count = 0
    while count < 1:
        try:
            count = int(input("Number of rounds: "))
        except ValueError:
            pass

    #collect the three keys for every round
    rounds = []
    for n in range(1, count + 1):
        print(f"Round {n}:")
        vkey = ask("  Vigenere keyword: ", letters=True)
        ckey = ask("  Column permutation key: ")
        rkey = ask("  Row permutation key: ")
        rounds.append((vkey, ckey, rkey))

    print()
    if mode == "e":
        result = encrypt(text, rounds)
        print(f"\nFinal ciphertext (text): {show(result)}")
        #hex is printed so it can be copied and pasted back in to decrypt
        print(f"Final ciphertext (hex, copy this to decrypt): {result.encode().hex()}")
    else:
        result = decrypt(text, rounds)
        print(f"\nRecovered plaintext: {result}")


if __name__ == "__main__":
    #keep running until the user says no
    while True:
        try:
            main()
        except (KeyboardInterrupt, EOFError):
            break
        except Exception as error:
            print(f"\nError: {error}")
        again = input("\nRun again? (y/n): ").strip().lower()
        if again != "y":
            break
        print("\n" + "=" * 40 + "\n")
    input("\nPress Enter to close...")

