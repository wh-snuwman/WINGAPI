import {wingAPI} from ".././wingAPI/src/script/wingAPI.JS"

(async () => {
    const wing = new wingAPI()
    await wing.connect('localhost',1270)


    // wing.send('ping',{'msg':'Hello wingAPI!'})
    const n = Math.floor(Date.now())
    
    wing.signup(`USER:${n}`,'1234')
    wing.login(`USER:${n}`,'1234')    

    wing.recv((data)=>{
    })

})();