# Storage layers

A storage layer is a stage in which jobs do not need to be processed, i.e.,
they do not have any processing times. Instead, the intervals are
constrained by intra-stage constraints.

Moreover, storage layers (in the application in compound feed production)
must take into account multi-level product characteristics to avoid
contamination of goods.

The machine layout conists of a set of production lines, each of whch
consists of one unrelated machine (i.e., storage) unit.

This model uses the following variables:

- $T_b$: interval variable for batch $b$
- $Tp_b$: interval variable for product $p$
- $Ap_{pi}$: interval assignment variable for product $p$ on machine $i$
- $Sp_i$: sequence variable of product assignment variables on machine $i$

We do not need to take into account batch assignment variables, since that is covered by the product assignment variables.

::: src.cp.storage_layer
