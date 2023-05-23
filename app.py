const express = require('express');
const mysql = require('mysql')
const app = express();
const path = require('path');
const bodyParser = require('body-parser');
const {logger} = require('./middleware/logEvents.js');
const { appendFileSync } = require('fs');
const { error } = require('console');
var router = express.Router()
var multer = require('multer');
var upload = multer({dest:'public/static/'});




const PORT = process.env.PORT || 3305;

var con = mysql.createConnection({
    host: "localhost",
    user: "Jack",
    password: 'rootAPPLE',
    database: "owo",
});

app.set('view engine', 'html');
app.use(express.static("public"));
app.use(express.json());
app.use(logger)
app.use(bodyParser.urlencoded({ extended: true })); 
app.engine('html', require('ejs').renderFile);

var storage = multer.diskStorage({
  destination: function (req, file, cb) {
    cb(null, "public/static")
  },
  filename: function (req, file, cb) {
    cb(null, "-" + file.originalname)
  }
})

var upload = multer({ storage: storage })


app.get('/admin', function(req, res)  {
  sql = "SELECT * FROM products" ;
  con.query(sql, function (err, result, next) {
    let rows = JSON.parse(JSON.stringify(result))  
    res.render(__dirname + "/veiws/admin.html", {
      ID: rows });
  });
});

app.get('/index',(req,res)=>
{ res.sendFile(path.join(__dirname,'veiws','index.html'))
});

app.post("/create", (req, res) => {
    res.status(404).sendFile((path.join(__dirname,'veiws','404.html')))
    let firstname = (`${req.body.first_name}`)
    let lastname = (`${req.body.last_name}`)
    sql = "INSERT INTO profiles (first_name, last_name) VALUES ('"+firstname+"', '"+lastname+"')";
    con.query(sql, function (err, result) {
        if (err) throw err;
        console.log("1 record inserted");
  });
})

app.post("/img",  upload.single('tomato'), function (req, res, next) {
  sql = "INSERT INTO profiles (img) VALUES ('"+file+"')";
    con.query(sql, function (err, result) {
        if (err) throw err;
        console.log("1 record inserted");
  });
})



app.get('/',(req,res)=>
{ res.sendFile(path.join(__dirname,'veiws','Homepage.html'))
});

app.post('/ID',(req,res)=> { 
  sql = "SELECT * FROM products" ;
  let data = req.body.shit
  let number = data -= 1
  con.query(sql, function (err, result, next) {
    let e = JSON.parse(JSON.stringify(result))  
    ID_value = e[number]
    res.render(__dirname + "/veiws/product.html", {
      yes: ID_value });
  });
})



app.get('/*', (req,res) => {
    res.status(404).sendFile((path.join(__dirname,'veiws','404.html')))
});

const url = 'https://www.webmound.com/uploads/26/banner.jpg';


app.listen(PORT, () => console.log('server is running'));

