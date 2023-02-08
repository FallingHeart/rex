# rex

## git commit

vx.x.x

## clean

python setup.py sdist

## release

python setup.py upload --verbose

## install

pip intall rext

## upgrade

pip install --upgrade rext

## upgrade 指定版本

pip install --upgrade rext==0.1.22

## 镜像会同步不及时，临时使用默认镜像更新

pip install -i https://pypi.org/simple --upgrade rext

## list

pip list

## import

from rext import mstring as ms

## use

print(ms.remove_space_all("666 666"))
