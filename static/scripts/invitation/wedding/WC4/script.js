var tl=gsap.timeline()
tl.from(".bg-top-left",{
    y:-200,
    opacity:0,
})
tl.from(".bg-top-right",{
    y:-200,
    opacity:0,
})

tl.from(".title",{
    y:-200,
    opacity:0,
    scale:0.5,
    delay:0.3,
    stagger:0.2
})
tl.from(".name",{
    y:-200,
    opacity:0,
    stagger:0.2
})
tl.from(".and",{
    y:200,
    opacity:0,
})



tl.from(".content h1",{
    x:200,
    opacity:0,
    stagger:0.2
})


tl.from(".info h3",{
    y:-200,
    opacity:0,
})


tl.from(".month",{
    y:-200,
    opacity:0,
    scale:0.5
})


tl.from(".address",{
    x:-400,
    opacity:0,
    scale:0.8
})



tl.from(".div-container .date",{
    y:-200,
    opacity:0,
    scale:0.5
})


tl.from(".div-container .address",{
    y:-200,
    opacity:0,
    scale:0.5
})

tl.from(".bg-bottom-right",{
    x:200,
    opacity:0,
})
tl.from(".bg-bottom-left",{
    x:-200,
    opacity:0,
})