//worker.js
importScripts('https://cdn.jsdelivr.net/npm/dohjs@0.3.1/dist/doh.js');
var delais = 0;
var sites = [];
var Types = [];
var resolver = null;
var TTrequests = 0;
var TTrequestsNO = 0;
var index = 0;
var max = 0;
var Interval = null;

self.addEventListener('message', function (e) {
    if (e.data.cmd == "stop") {
        self.close();
    } else if (e.data.cmd == "start") {
        delais = e.data.delais;
        sites = e.data.sites;
        Types = e.data.Types;
        resolver = new doh.DohResolver(e.data.resolverUrl);
        this.setInterval(sendAdvance, 1000);
        index = getRandomInt(sites.length);
        max = sites.length;
        Interval = setInterval(generateTraffic, delais);
    }
});

function generateTraffic() {
    Types.forEach(Type => {
        resolve(index, Type);
    });
    index++;
    if (index >= max) {
        index = 0;
    }
}

function sendAdvance() {
    self.postMessage({ cmd: "addStats", TTrequests: TTrequests, TTrequestsNO: TTrequestsNO });
    TTrequestsNO = 0;
    TTrequests = 0;
}

//récupération d'un entier entre 0 et max
function getRandomInt(max) {
    return Math.floor(Math.random() * max);
}

//récupération du record dns Type pour le site a la position rand dans la liste sites via doh
async function resolve(rand, Type) {
    response = await resolver.query(sites[rand], Type, "GET", { "cache-control": "no-store", "cache-control": "no-cache" }).catch(e => { TTrequestsNO++; log(e); })
    TTrequests++;
    return
}

function log(message) {
    self.postMessage({ cmd: "log", log: message });
}
