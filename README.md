# Transaction tree analysis

The main part of this repository under active development is the `ringxor` library, for recording edges of the transaction tree revealed by differ-by-one ring pairs.

Suppose we have the sets {2, 4, 8} and {2, 4, 10}. We'll say that this pair has a "differ by one" (DBO) relationship, because singleton 8 sticks out on the left, and the singleton 10 sticks out on the right. 

Any pair of rings whose members differ by only one element will be called a "DBO ring pair". We'll refer to any ring that belongs to any DBO pair as a "DBO ring". (Note that one DBO ring can be in many DBO pairs, and this is disturbingly common on the Monero blockchain)

## intERtransaction DBO pairs
We can have DBO ring pairs across different transactions, for example:
+ [https://xmrchain.net/tx/6fb06bcd042e5f705a458a37cc3aaf6a1ad7a35657cf03f74e3aea383a47fb7e](https://xmrchain.net/tx/6fb06bcd042e5f705a458a37cc3aaf6a1ad7a35657cf03f74e3aea383a47fb7e)
+ [https://xmrchain.net/tx/4509d22833ca47ec224fcd226626bc830056d39a6ff1278c56a4796645c47859](https://xmrchain.net/tx/4509d22833ca47ec224fcd226626bc830056d39a6ff1278c56a4796645c47859)

Here is another more extreme example, with dozens of DBO ring pairs across just two many-input transactions:
+ [https://xmrchain.net/tx/71879ba6099ea18d456cd31694b0860f3649ebeb28ce5630ccb1be312c0cc8cb](https://xmrchain.net/tx/71879ba6099ea18d456cd31694b0860f3649ebeb28ce5630ccb1be312c0cc8cb)
+ [https://xmrchain.net/tx/48ab24a942778d0c7d79d8bbc7076329ae45b9b7c8cc7c15d105e135b4746587](https://xmrchain.net/tx/48ab24a942778d0c7d79d8bbc7076329ae45b9b7c8cc7c15d105e135b4746587)

_(as an aside, there are many oddities in the above pair, such as the incorrect decoy selection algorithm for most of the rings (old clusters, and then one new output), and the fact that the 4th ring does appear to be sampled from the correct distribution?)_

## intRAtransaction DBO pairs
We also find many examples of DBO ring pairs within the same transaction, for example:
+ Mitchell put a link here! 


## DBO ring analysis
By removing transaction labels we can automatically detect intertransaction and intratransaction DBO relationships in a single pass. 

If R is the number of rings on the blockchain, to make each pairwise comparison we would naively expect to do R^2 checks

However, we do not need to check along the diagonal of the matrix, because a ring cannot be a DBO ring pair with itself. So we can reduce the number of checks to R^2 - R

Furthermore, because ring xor is symmetric, we only need to look at the upper triangle of the matrix! This brings us down to (R^2-R)/2 checks.

This process is "embarrassingly parallel", and this library implements CPU multithreading. 

## Acknowledgements

`nioc` initially noticed the intRAring DBO pairs

`rucknium` brought my attention to some transactions that turned out to exhibit intERring DBO pairs