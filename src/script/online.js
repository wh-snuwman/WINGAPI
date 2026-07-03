import {wingAPI} from ".././wingAPI/src/script/wingAPI.JS"

(async () => {
    const wing = new wingAPI()
    await wing.connect('ws://localhost:4000')


    wing.recv((data)=>{
    })

})();