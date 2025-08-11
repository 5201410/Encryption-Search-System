## Encryption-Search-System

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
    git clone https://github.com/5201410/Encryption-Search-System.git
    cd Encryption-Search-System
    pip3 install -r requirements.txt 
    ```


## File Structure

```
.
├── README.md
├── requirements.txt
|
├── app.py // 启动程序
├── Conjunctive.py // 合取查询
├── Disjunctive.py // 析取查询
├── Boolean.py // 布尔查询
|
├── data // 数据集
│   ├── enron_index0.csv // 10^2 key/value pairs
│   ├── enron_index1.csv // 10^3 key/value pairs
│   ├── enron_index2.csv // 10^4 key/value pairs
│   ├── enron_index3.csv // 10^5 key/value pairs
│   ├── enron_inverted0.csv
│   ├── enron_inverted1.csv
│   ├── enron_inverted2.csv
│   ├── enron_inverted3.csv
|   ├── ...
|
├── Utils // 工具集
│   ├── BF.py 
│   ├── SHVE.py 
│   ├── SSPE_XF.py
│   ├── TSet.py
│   ├── XorFilter.py
│   ├── cfg.py
│   ├── cryptoUtils.py
│   ├── fileUtils.py
│   ├── pbcUtils.py
|
```
本系统是在研究并学习了相关密文检索方案及其程序后，经过改进和创新后的成果，只针对于自主研究和学习，并感谢所有其他方案的作者以及
开源作者，对所有为本项目努力的老师和朋友表示感谢o( ❛ᴗ❛ )o  o( ❛ᴗ❛ )o
