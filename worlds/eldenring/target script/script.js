fs = require('fs');

var output = ''
var shoplots = {} // [name: lot]

fs.readFile('./targets.txt', 'utf8', function (e, data) {
    split = data.split("\n")
    split.forEach(line => {
        if(line.startsWith("\"")){
            lot = line.split("(")
            shoplots[line.slice(1, line.lastIndexOf("\""))] = lot[lot.length - 1].slice(0, lot[lot.length - 1].lastIndexOf("\'")+1)
        }else{
            lot = line.split("(")
            shoplots[line.slice(1, line.indexOf("\':"))] = lot[lot.length - 1].slice(0, lot[lot.length - 1].lastIndexOf("\'")+1)
        }
    });

    // console.log(shoplots)
});

fs.readFile('./location table.txt', 'utf8', function (e, data) {

    split = data.split("\n"); 
    split.forEach(line => {
        if(line.includes("ERLocationData") && !line.includes("targets=")){
            included = false
            Object.keys(shoplots).forEach(lot => {
                if(line.includes(lot) && !included){
                    start = line.slice(0, line.lastIndexOf(")"))
                    end = line.slice(line.lastIndexOf(")"), line.length)
                    output += `${start}, targets=(${shoplots[lot]})${end}`
                    included = true
                }
            });
            if(!included){output += line}
        }else{
            output += line
        }
        output +="\n"
    });
    
    // console.log(output)

    fs.writeFileSync('./location table output.txt', output)
});



