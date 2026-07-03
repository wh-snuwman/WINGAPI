import {wingAPI} from "../.././wingAPI/src/script/wingAPI.js"

(async () => {
    const wing = new wingAPI()
    await wing.connect('ws://localhost:4000')

    const n = Math.floor(Date.now())
    
    wing.signup(`USER:${n}`,'1234')
    

    wing.signupOk(()=>{
        wing.login(`USER:${n}`,'1234')    
    })
    
    wing.loginOk(()=>{
        console.log('asd')
        wing.joinGroup('daehogang')
        wing.leftGroup('daehogang')
        
    })

    wing.recv((data)=>{
        
    })

})();