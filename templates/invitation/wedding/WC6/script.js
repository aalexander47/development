var tl=gsap.timeline()
tl.from(".topleft-img ",{
    x:200,
    opacity:0,
})
tl.from("h1",{
    y:-200,
    opacity:0
})
tl.from("h2",{
   scale:0.2,
    y:-400,
    opacity:0,
})

tl.from(".couple ",{
    y:-200,
    opacity:0,
    scale:0.5,

})
tl.from(".names",{
    y:-200,
    opacity:0,
    scale:0.5,
})

tl.from(".date-container",{
    stagger:0.2,
    y:-200,
    opacity:0,
    scale:0.5,
   
})

tl.from(".venue",{
    stagger:0.2,    
    y:-200,
    opacity:0,
    scale:0.5
})
tl.from(".bottomright-img",{
    x:-200,
    opacity:0,
    stagger:0.2
})
