# Doris

This repo shows the constructions of OXT [1], HXT[2], ConjFilter[3] and Doris[4].

## Environment Configuration

- ubuntu20.04
- python3.8
- [pypbc](https://github.com/debatem1/pypbc)
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
├── Doris_XF_new.py
├── Doris_XF_Boolean.py
├── Doris_XF.py
├──
|
├── data // database of enron and enwiki, including indexes and inverted indexes
│   ├── enron_index0.csv // 10^2 key/value pairs
│   ├── enron_index1.csv // 10^3 key/value pairs
│   ├── enron_index2.csv // 10^4 key/value pairs
│   ├── enron_index3.csv // 10^5 key/value pairs
│   ├── enron_index4.csv // 10^6 key/value pairs
│   ├── enron_inverted0.csv
│   ├── enron_inverted1.csv
│   ├── enron_inverted2.csv
│   ├── enron_inverted3.csv
│   ├── enron_inverted4.csv
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
|
```


