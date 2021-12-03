# rex

## clean

python setup.py sdist

## release

python setup.py upload --verbose

## install

pip intall rext

## upgrade

pip install --upgrade rext

## list

pip list

## import

from rext import str_manage as sm

## use

print(sm.remove_space("666 666"))
