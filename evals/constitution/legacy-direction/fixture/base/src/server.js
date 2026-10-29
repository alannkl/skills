const express = require('express');

const app = express();
app.use(express.json());
app.use('/customers', require('./routes/customers'));
app.use('/orders', require('./routes/orders'));
app.use('/products', require('./routes/products'));
app.use('/carts', require('./routes/carts'));
app.use('/users', require('./routes/users'));

app.listen(process.env.PORT || 3000);
