

// Windows functions:
window.addEventListener("load", init, true); 
async function init(){
    emptyAllSpans();
    overview();
    stockinformation();
    getStocksExistinginDb();
    getStocksForVisu();
    getTables();
} 


// Api-call functions:
async function getCall(url = ""){
    const response = await fetch(url,{
        method: 'GET', // *GET, POST, PUT, DELETE, etc.
        mode: 'cors', // no-cors, *cors, same-origin
        credentials: 'same-origin', 
        headers: {
          'Content-Type': 'application/json'
        }
    });
    const data = await response.json()
    return data
}


// Onload functions:
async function overview(){
    const url = `http://127.0.0.1:8000/overview`
    const data = await getCall(url)
    const stock = data.stock
    const keyword = data.keyword
    const days = data.days
    const rows = data.rows
    overwriteOverview(stock,keyword,days,rows)
}

async function stockinformation(){
    const url = `http://127.0.0.1:8000/stockinformation`
    const data = await getCall(url)
    const symbols = data.symbols
    const stocknames = data.stocknames
    stocklistForScraping(symbols, stocknames)
}

function stocklistForScraping(symbols,stocknames){
    for (var i = 0; i < symbols.length; i++){
        var x = document.createElement("OPTION");
        x.setAttribute("value", symbols[i]);
        x.setAttribute("id", symbols[i]);
        var t = document.createTextNode(stocknames[i]);
        x.appendChild(t);
        document.getElementById("scrapestock").appendChild(x);
    }
}

async function getStocksExistinginDb(){
    const url = `http://127.0.0.1:8000/getstocks`
    const data = await getCall(url)
    const symbols = data.symbols
    const stocknames = data.stocknames
    console.log(symbols)
    console.log(stocknames)
    stocklistForModel(symbols,stocknames)
}

async function getStocksForVisu(){
    const url = `http://127.0.0.1:8000/getstocksvisu`
    const data = await getCall(url)
    const symbols = data.symbols
    const stocknames = data.stocknames
    console.log(symbols)
    console.log(stocknames)
    stocklistForvisu(symbols,stocknames)
}


async function getTables(){
   // const url = `http://127.0.0.1:8000/tables`
   // const data = await getCall(url)
   // const tables = data.tables
   tables = ["twitterdata","stockdata"]
    tableList(tables)
    
}

// Scrap-form functions:
async function scrape(){
    const scrapekeyword = document.getElementById("scrapekeyword");
    const select = document.getElementById("scrapestock");
    const scrapestock = select.options[select.selectedIndex].value;
    const scrapestartdate = document.getElementById("scrapestartdate");
    const scrapeenddate = document.getElementById("scrapeenddate");
    const url = `http://127.0.0.1:8000/scrape/`+scrapekeyword.value+`/`+scrapestock+`/`+scrapestartdate.value+`/`+scrapeenddate.value
    const data = await getCall(url)
    const stock = data.stock
    const keyword = data.keyword
    const days = data.days
    const rows = data.rows
    deleteNnStockList()
    deletevisuStockList()
    getStocksExistinginDb();
    getStocksForVisu();
    overwriteOverview(stock,keyword,days,rows)
  }
 function overwriteOverview(stock,keyword,days,rows){
     const oldstock = document.getElementById("stock")
     oldstock.innerText = stock
     const oldkeyword = document.getElementById("keyword")
     oldkeyword.innerText = keyword
     const olddays = document.getElementById("days")
     olddays.innerText = days
     const oldrows = document.getElementById("rows")
     oldrows.innerText = rows
 }

// LSTM-form functions:
function stocklistForModel(symbols,stocknames){
    for (var i = 0; i < symbols.length; i++){
        var x = document.createElement("OPTION");
        x.setAttribute("value", symbols[i]);
        x.setAttribute("id", symbols[i]);
        var t = document.createTextNode(stocknames[i]);
        x.appendChild(t);
        document.getElementById("nnstock").appendChild(x);
    }
    const select =  document.getElementById("nnstock")
    select.onchange = async function(event){
        const stock = select.options[select.selectedIndex].value;
        if(stock!= "NAN"){
            const url = `http://127.0.0.1:8000/getscrape/`+stock
            const data = await getCall(url)
            const dropurl = `http://127.0.0.1:8000/dropcolumlist`
            await getCall(dropurl)
            deleteColumnList()
            deleteGoalvariabList()
            const scrapekeywords = data.scrapekeywords
            console.log(scrapekeywords)
            keywordlistForModel(scrapekeywords)  
        }
    }
}

function deleteNnStockList(){
    const select =  document.getElementById("nnstock")
    if (select.options.length > 0){
        var i, L = select.options.length - 1;
        for(i = L; i >= 0; i--) {
           select.remove(i);        
        }
    }
}

function keywordlistForModel(scrapekeywords){
    const select =  document.getElementById("nnkeyword")
    if (select.options.length > 0){
        var i, L = select.options.length - 1;
        for(i = L; i >= 0; i--) {
          select.remove(i);        
        }
    }
    for (var i = 0; i < scrapekeywords.length; i++){
        var x = document.createElement("OPTION");
        x.setAttribute("value", scrapekeywords[i]);
        x.setAttribute("id", scrapekeywords[i]);
        var t = document.createTextNode(scrapekeywords[i]);
        x.appendChild(t);
        document.getElementById("nnkeyword").appendChild(x);
    }
    select.onchange = async function(event){
        const keyword = select.options[select.selectedIndex].value;
        if(keyword != "Your database is empty, please scrape first!"){
            const url = `http://127.0.0.1:8000/createdataframeformodel/`+keyword
            const data = await getCall(url)
            const dropurl = `http://127.0.0.1:8000/dropcolumlist`
            await getCall(dropurl)
            deleteColumnList()
            deleteGoalvariabList()
            const columns = data.columns
            console.log(columns)
            columlistForModel(columns)
        }
    }
}

function columlistForModel(columns){
    const select =  document.getElementById("nnselectcolumns")
    for (var i = 0; i < columns.length; i++){
        var x = document.createElement("OPTION");
        x.setAttribute("value", columns[i]);
        x.setAttribute("id", columns[i]);
        var t = document.createTextNode(columns[i]);
        x.appendChild(t);
        select.appendChild(x);
    }
    select.onclick = async function(event){
        const colum = select.options[select.selectedIndex].value;
        const url = `http://127.0.0.1:8000/selectecolumn/`+colum
        select.options[select.selectedIndex].remove();
        const data = await getCall(url)  
        const length = data.length
        goalvariablelistForModel(colum)
        if (length == 0){
            deleteGoalvariabList()
        }     
    }    
}

function deleteColumnList(){
    const select =  document.getElementById("nnselectcolumns")
    if (select.options.length > 0){
        var i, L = select.options.length - 1;
        for(i = L; i >= 0; i--) {
           select.remove(i);        
        }
    }
}

function goalvariablelistForModel(colum){
    const select =  document.getElementById("nngoalvariable")
    var x = document.createElement("OPTION");
    x.setAttribute("value", colum);
    x.setAttribute("id", colum);
    var t = document.createTextNode(colum);
    x.appendChild(t);
    select.appendChild(x);
    select.onchange = async function(event){
        const goalvariab = select.options[select.selectedIndex].value;
        if(stock!= "NAN"){
            const url = `http://127.0.0.1:8000/selectegoalvariable/`+goalvariab
            await getCall(url)
        }
    }

}

function deleteGoalvariabList(){
    const select =  document.getElementById("nngoalvariable")
    if (select.options.length > 0){
        var i, L = select.options.length - 1;
        for(i = L; i >= 0; i--) {
           select.remove(i);        
        }
    }
}

function randomfeatures(){
    const select =  document.getElementById("nnrandomfeature")
    if (select.checked){
        const url = `http://127.0.0.1:8000/randomcolums/`+true
        getCall(url)
    }else{
        const url = `http://127.0.0.1:8000/randomcolums/`+false
        getCall(url)
    }
}

function randomHyperparams(){
    const select =  document.getElementById("nnrandomhyperparam")
    if (select.checked){
        const url = `http://127.0.0.1:8000/randomhyperparams/`+true
        getCall(url)
    }else{
        const url = `http://127.0.0.1:8000/randomhyperparams/`+false
        getCall(url)
    }
}

function runLstm(){
    const epochs = document.getElementById("nnepochs");
    const layers = document.getElementById("nnlayer");
    const dropout = document.getElementById("nndropout");
    const lerning = document.getElementById("nnlerningrate");
    const hidden = document.getElementById("nnhiddensize");
    const randomcolums = document.getElementById("nnrandomfeature")
    const randomhyper = document.getElementById("nnrandomhyperparam")
    const url = `http://127.0.0.1:8000/trainmodel/`+epochs.value+`/`+layers.value+`/`+dropout.value+`/`+lerning.value+`/`+hidden.value
    getCall(url) 
    epochs.value = '';
    layers.value = '';
    hidden.value = '';
    randomcolums.checked = false
    randomhyper.checked = false
    deleteGoalvariabList()
    deleteColumnList()
    alert("Das Training ihres Models hat begonnen!")
}


// Visualisation
function stocklistForvisu(symbols,stocknames){
    for (var i = 0; i < symbols.length; i++){
        var x = document.createElement("OPTION");
        x.setAttribute("value", symbols[i]);
        x.setAttribute("id", symbols[i]);
        var t = document.createTextNode(stocknames[i]);
        x.appendChild(t);
        document.getElementById("visustock").appendChild(x);
    }
    const select =  document.getElementById("visustock")
    select.onchange = async function(event){
        const stock = select.options[select.selectedIndex].value;
        if(stock!= "NAN"){
            const url = `http://127.0.0.1:8000/getscrapevisu/`+stock
            const data = await getCall(url)
            const dropurl = `http://127.0.0.1:8000/dropcolumlistvisu`
            await getCall(dropurl)
            deleteVisuColumnList()
            const scrapekeywords = data.scrapekeywords
            console.log(scrapekeywords)
            keywordlistForVisu(scrapekeywords)  
        }
    }
}

function deletevisuStockList(){
    const select =  document.getElementById("visustock")
    if (select.options.length > 0){
        var i, L = select.options.length - 1;
        for(i = L; i >= 0; i--) {
           select.remove(i);        
        }
    }
}

function deleteVisuColumnList(){
    const select =  document.getElementById("visuselectcolumns")
    if (select.options.length > 0){
        var i, L = select.options.length - 1;
        for(i = L; i >= 0; i--) {
           select.remove(i);        
        }
    }
}

function keywordlistForVisu(scrapekeywords){
    const select =  document.getElementById("visuscrape")
    if (select.options.length > 0){
        var i, L = select.options.length - 1;
        for(i = L; i >= 0; i--) {
           select.remove(i);        
        }
    }
    for (var i = 0; i < scrapekeywords.length; i++){
        var x = document.createElement("OPTION");
        x.setAttribute("value", scrapekeywords[i]);
        x.setAttribute("id", scrapekeywords[i]);
        var t = document.createTextNode(scrapekeywords[i]);
        x.appendChild(t);
        select.appendChild(x);
    }
    select.onchange = async function(event){
        const keyword = select.options[select.selectedIndex].value;
        if(keyword != "Your database is empty, please scrape first!"){
            const url = `http://127.0.0.1:8000/createdataframeforvisu/`+keyword
            const data = await getCall(url)
            const dropurl = `http://127.0.0.1:8000/dropcolumlistvisu`
            await getCall(dropurl)
            deleteVisuColumnList()
            const columns = data.columns
            console.log(columns)
            columlistForVisu(columns)
        }
    }
}

function columlistForVisu(columns){
    const select =  document.getElementById("visuselectcolumns")
    for (var i = 0; i < columns.length; i++){
        var x = document.createElement("OPTION");
        x.setAttribute("value", columns[i]);
        x.setAttribute("id", columns[i]);
        var t = document.createTextNode(columns[i]);
        x.appendChild(t);
        select.appendChild(x);
    }
 //   select.onclick = async function(event){
   //     const colum = select.options[select.selectedIndex].value;
     //   const url = `http://127.0.0.1:8000/selectecolumn/`+colum
       // select.options[select.selectedIndex].remove();
        //const data = await getCall(url)  
        //const length = data.length
        //goalvariablelistForModel(colum)
        //if (length == 0){
        //    deleteGoalvariabList()
        //}     
    //}    
}

// Overview Database

function tableList(tables){
    const select =  document.getElementById("ovtable")
    for (var i = 0; i < tables.length; i++){
        var x = document.createElement("OPTION");
        x.setAttribute("value", tables[i]);
        x.setAttribute("id", tables[i]);
        var t = document.createTextNode(tables[i]);
        x.appendChild(t);
        select.appendChild(x);
    }
    select.onchange = async function(event){
        const table = select.options[select.selectedIndex].value;
        if(table!= "NAN"){
            const url = `http://127.0.0.1:8000/table/`+table
            const data = await getCall(url)
            deleteOvKeyworList()
            const symbols = data.symbols
            const name = data.stockname
            keywordlistForOv(symbols,name)
        }
    }
}

function keywordlistForOv(keywords,name){
    const select =  document.getElementById("ovkeyword")
    if (select.options.length > 0){
        var i, L = select.options.length - 1;
        for(i = L; i >= 0; i--) {
           select.remove(i);        
        }
    }
    for (var i = 0; i < keywords.length; i++){
        var x = document.createElement("OPTION");
        x.setAttribute("value", keywords[i]);
        x.setAttribute("id", keywords[i]);
        var t = document.createTextNode(name[i]);
        x.appendChild(t);
        select.appendChild(x);
    }
    select.onchange = async function(event){
        const keyword = select.options[select.selectedIndex].value;
        if(keyword != "NAN"){
            const url = `http://127.0.0.1:8000/table/information/`+keyword
            const data = await getCall(url)
            const keywo = data.keywo
            const days = data.days
            const rows = data.rows
            const values = data.values
            ov(keywo,days,rows,values)        }
    }
}

function ov(keywo,days,rows,values){
    const oldkeywo = document.getElementById("ovskeyword")
    oldkeywo.innerText = keywo
    const olddays = document.getElementById("ovsdays")
    olddays.innerText = days
    const oldrows = document.getElementById("ovsrows")
    oldrows.innerText = rows
    const oldvalue = document.getElementById("ovsvalues")
    oldvalue.innerText = values
}

function deleteOvKeyworList(){
    const select =  document.getElementById("ovkeyword")
    if (select.options.length > 0){
        var i, L = select.options.length - 1;
        for(i = L; i >= 0; i--) {
           select.remove(i);        
        }
    }
}


async function initdb(){
    const url = `http://127.0.0.1:8000/initdatabase`
    await getCall(url)
    stockinformation();
}


function emptyAllSpans(){
    const oldkeywo = document.getElementById("ovskeyword")
    oldkeywo.innerText = ""
    const olddays = document.getElementById("ovsdays")
    olddays.innerText = ""
    const oldrows = document.getElementById("ovsrows")
    oldrows.innerText = ""
    const oldvalue = document.getElementById("ovsvalues")
    oldvalue.innerText = ""
    const oldstock = document.getElementById("stock")
    oldstock.innerText = ""
    const oldkeyword = document.getElementById("keyword")
    oldkeyword.innerText = ""
    const oldday = document.getElementById("days")
    oldday.innerText = ""
    const oldrow = document.getElementById("rows")
    oldrow.innerText = ""
}