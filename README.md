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
    git clone https://github.com/5201410/Encryption-Search-System.git
    cd Encryption-Search-System
    pip3 install -r requirements.txt 
    ```
相关的界面进入指令和步骤在文档第四章4.2功能展示部分详细说明

## File Structure

```
.
├── README.md
├── requirements.txt
|
├── Disjunctive.py //disjunctive query
├── Boolean.py //boolean query
├── Conjunctive.py //conjunctive query
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


