import {wingAPI} from ".././wingAPI/src/script/wingAPI.JS"

(async () => {
    const wing = new wingAPI()
    await wing.connect('localhost',1270)


    wing.send('ping',{'msg':'Hello wingAPI!'})

    wing.signup('Mrhello','1234')

    wing.recv((data)=>{
    })

})();