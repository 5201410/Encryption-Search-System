- ubuntu20.04
- python3.8
- [pypbc](https://github.com/5201410/Encryption-Search-System-)
    ```sh
    # install requirements libraries
    sudo apt update 
    sudo apt-get install flex bison libgmp-dev make

    # Download PBC source code and compile it
    cd ~ &&
    wget https://crypto.stanford.edu/pbc/files/pbc-0.5.14.tar.gz &&
    tar -xf pbc-0.5.14.tar.gz &&
    cd pbc-0.5.14 &&
    ./configure --prefix=/usr --enable-shared &&
    make &&
    sudo make install &&
    cd .. 

    # re-configure the ldconfig
    sudo ldconfig

    # Install the pypbc
    git clone https://github.com/debatem1/pypbc &&
    cd pypbc &&
    sudo pip3 install .
    cd ..
    ```
- install source code and additional python libraries
    ```sh
    git clone https://github.com/CDSecLab/Doris.git
    cd Doris
    pip3 install -r requirements.txt 
    ```


## File Structure

```
.
├── README.md
├── requirements.txt
|
| // the constructions of OXT, HXT, ConjFilter and Doris
├── Doris_XF_new.py //disjunctive query
├── Doris_XF_Boolean.py //boolean query
├── Doris_XF.py //conjunctive query
├── app.py //main beginning
|
├── data // database of enron and enwiki, including indexes and inverted indexes
│   ├── enron_index0.csv // 10^2 key/value pairs
│   ├── enron_index1.csv // 10^3 key/value pairs
│   ├── enron_inverted0.csv
│   ├── enron_inverted1.csv
|   ├── ...
|
├── Utils 
│   ├── BF.py 
│   ├── SHVE.py 
│   ├── SSPE_XF.py
│   ├── TSet.py
│   ├── XorFilter.py
│   ├── cfg.py
│   ├── cryptoUtils.py
│   ├── fileUtils.py
│   ├── pbcUtils.py
│   └── test // examples and tests of tools





## Reference

[1]. David Cash, Stanislaw Jarecki, Charanjit S. Jutla, Hugo Krawczyk, Marcel-Catalin Rosu, Michael Steiner: Highly-Scalable Searchable Symmetric Encryption with Support for Boolean Queries. CRYPTO 2013: 353-373.

[2]. Shangqi Lai, Sikhar Patranabis, Amin Sakzad, Joseph K. Liu, Debdeep Mukhopadhyay, Ron Steinfeld, Shifeng Sun, Dongxi Liu, Cong Zuo: Result Pattern Hiding Searchable Encryption for Conjunctive Queries. CCS 2018: 745-762.

[3]. Sarvar Patel, Giuseppe Persiano, Joon Young Seo, Kevin Yeo: Efficient Boolean Search over Encrypted Data with Reduced Leakage. ASIACRYPT 2021: 577-607.

[4]. Yunling Wang, Shi-Feng Sun, Jianfeng Wang, Xiaofeng Chen, Joseph K.Liu, and Dawu Gu. Practical Non-interactive Encrypted Conjunctive Search with Leakage Suppression. CCS 2024.
