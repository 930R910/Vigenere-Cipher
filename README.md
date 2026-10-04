# Vigenère Cipher with Row & Column Permutations

A multi-round Vigenère cipher written in Python 3 (standard library only).
Each round is **Vigenère substitution → column permutation → row permutation**, and as many rounds as you want can be chained.
Decryption reverses every step, so pasting the ciphertext back in restores the exact original text.

## How to compile / run
Python 3.8 or newer is required. Nothing needs to be compiled and no libraries need to be installed.

```
python vigenere_cipher.py
```

The program asks for, in this order:
1. **Mode**: `e` (encrypt) or `d` (decrypt)
2. **Text**: the plaintext (a word or phrase), or the hex ciphertext when decrypting
3. **Number of rounds** (1 or more)
4. For each round:
   - the **Vigenère keyword** (letters)
   - the **column permutation key** (digits like `3142`, or a word like `ZEBRA`)
   - the **row permutation key** (digits like `21`, or a word)

To decrypt, paste the hex ciphertext and enter the **same keys in the same order** that were used to encrypt.

## Output
The program prints the result of every step in the terminal: for each round the Vigenère result, the column permutation result and the row permutation result. At the end it prints the final ciphertext as text and as **hex**.

* The **hex** string is the one to copy and paste into decrypt mode. Hex keeps spaces and symbols exact, so nothing gets lost when copying.
* A space is shown as `_` in the printed results so it can be seen.
* After each run the program asks `Run again? (y/n)` and waits for Enter before closing.

## How the multi-round logic is structured
```
plaintext → [Vigenère → Columns → Rows]   round 1
          → [Vigenère → Columns → Rows]   round 2
          → ...                           → ciphertext
```

1. **Vigenère substitution**: every letter is shifted by the matching letter of the keyword, `(letter + shift) mod 26` (A=0 … Z=25). The keyword repeats and only advances on letters. Case, spaces, digits and punctuation are kept as they are.
2. **Column permutation**: the text is written in rows under the key (the grid width is the key length), then read column by column in the order given by the key.
3. **Row permutation**: the text is cut into rows of the same width, and the rows are reordered in groups of `len(row key)` rows. Only complete groups are reordered; leftover rows at the end stay where they are.

Each round has its own three keys.

### Permutation keys
The columns/rows are read in the **sorted order** of the key characters (ties go left to right). Only the order matters, not the size of the numbers.
With `3142`, the column marked 1 is read first, then 2, 3, 4. A word such as `ZEBRA` works the same way (A first, then B, E, R, Z).

Example, column key `3142` on `ABCDEFGH`:
```
 3 1 4 2
 A B C D
 E F G H      read columns 1,2,3,4 → B F | D H | A E | C G → "BFDHAECG"
```

Example, row key `21` on `ABCDEFGH` with width 4 (two rows swap places):
```
 A B C D          E F G H
 E F G H    →     A B C D      → "EFGHABCD"
```

### When a key does not change anything
* **Row key already in order** (`12`, `123`, `19`) keeps the rows where they are. Use something like `21` or `312`.
* **Row key of one digit** (`1`) has nothing to swap.
* **Column key of one digit** (`1`) makes a single column, so the text stays the same.
* **Not enough rows**: the text must fill at least 2 full rows of the grid for a row permutation to move anything, and at least as many full rows as the row key length for a complete group. A very long column key (wide grid) on a short text leaves only one row.

A column key like `3142` or `2413` and a row key like `21` or `312` are good choices.

## How it is reversed (symmetric reversibility)
Every permutation is stored as a list `p` meaning `new[j] = old[p[j]]`.
To undo it, every character is put back where it came from: `old[p[j]] = new[j]`.
The Vigenère shift is subtracted instead of added.

Decryption goes through the rounds **backwards**, and inside each round the steps are undone in reverse order:

```
ciphertext → undo rows → undo columns → undo Vigenère    (last round)
           → undo rows → undo columns → undo Vigenère    (round before)
           → ... → plaintext
```

No padding is ever added, so the text length never changes and the original text comes back exactly.

## Example test cases (encryption and decryption)

**Test 1: two rounds**
Round 1: keyword `LEMON`, columns `3142`, rows `21`
Round 2: keyword `KEY`, columns `2413`, rows `21`

| Stage | Result |
|---|---|
| Plaintext | `ATTACK AT DAWN` |
| Round 1 Vigenère | `LXFOPV EF RNHR` |
| Round 1 Columns | `XV ROENLPFHF R` |
| Round 1 Rows | `OENLXV RPFHF R` |
| Round 2 Vigenère | `YILVBT BTDRJ P` |
| Round 2 Columns | `L RYBT VBJITDP` |
| Round 2 Rows | `BT VL RYBJITDP` |
| **Ciphertext (hex)** | `425420564c205259424a49544450` |
| **Decrypted with the same keys** | `ATTACK AT DAWN` |

**Test 2: a phrase with punctuation, three rounds**
Round 1: `SECRET`, `ZEBRA`, `312`
Round 2: `KEY`, `4213`, `21`
Round 3: `CODE`, `321`, `231`

| Stage | Result |
|---|---|
| Plaintext | `Meet me at 9pm, dont be late!` |
| Round 1 Vigenère | `Eigk qx sx 9rd, hhfx dv ptli!` |
| Round 1 Columns | ` x,xpg rhviix9hdlksdf !Eq   t` |
| Round 1 Rows | `g rhviix9h x,xpdlksdf !Eq   t` |
| Round 2 Vigenère | `q vffmgh9l v,htbvoqnj !Ca   x` |
| Round 2 Columns | `vg tq!  mlho  fhvbnC qf9,vjax` |
| Round 2 Rows | `q!  vg t  fhmlho qf9vbnC,vjax` |
| Round 3 Vigenère | `s!  jj x  hvppjc tj9xpqG,xxdb` |
| Round 3 Columns | ` j vjtxGx!jxhp 9qxbs   pcjp,d` |
| Round 3 Rows | `xGx j vjt9qx!jxhp cjpbs   p,d` |
| **Ciphertext (hex)** | `784778206a20766a74397178216a78687020636a706273202020702c64` |
| **Decrypted with the same keys** | `Meet me at 9pm, dont be late!` |

**Test 3: one round**
Round 1: `KEY`, `21`, `21`

| Stage | Result |
|---|---|
| Plaintext | `HELLO WORLD` |
| Vigenère | `RIJVS UYVJN` |
| Columns | `IV YJRJSUVN` |
| Rows | ` YIVJSJRUVN` |
| **Ciphertext (hex)** | `205949564a534a5255564e` |
| **Decrypted with the same keys** | `HELLO WORLD` |

## Notes
- Decryption only works with the same keys, in the same order, that were used to encrypt.
- This is a classical cipher made for learning and is not secure for real data.
