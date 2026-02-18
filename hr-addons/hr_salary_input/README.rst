Salary Input
============

Features
--------

* Add Salary Inputs

* Add Inputs To  Contracts

* Get Sum Of inputs

Usage
-----
* open Payroll menu >> Configuration >> Salary Inputs

* Add Salary input  
    #. name
    #. code

* Go To Employee >>  Contract
  #. Create Contract

  #. Open Salary Input

  #. Select Salary Input, Add Value , Date From, Date To

    Value ==> value of Salary Input

    Date From ==> Start Date of Input

    Date To ==> End Date of input

Salary Rule
-----------
```python
result = contract.get_salary_inputs(payslip.date_from)
```
Credits
-------

.. |copy| unicode:: U+000A9 .. COPYRIGHT SIGN
.. |tm| unicode:: U+2122 .. TRADEMARK SIGN

- `Abdalla Mohamed <abdalla.mohamed@core-bpo.com>`_ |copy|
  `CORE B.P.O <http://www.core-bpo.com>`_ |tm| 2020
