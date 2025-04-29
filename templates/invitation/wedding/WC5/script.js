var tl=gsap.timeline()
tl.from(".bg-flower-top-left ",{
    x:200,
    opacity:0,
    stagger:0.2
})
tl.from(".bg-flower-top-right ",{
    x:-200,
    opacity:0,
    stagger:0.2
})

tl.from(".title",{
    y:-200,
    opacity:0,
    scale:0.5,
    delay:0.3,
    stagger:0.2
})
tl.from(".container h2",{
    x:-400,
    opacity:0,
})

gsap.from(".main, .text",{
    x:400,
    opacity:0,
    scale:0.5,
    stagger:0.2,

    scrollTrigger:{
        trigger:".main",
        scroller:"body",
        markers:true,
        start:"top 45%",
        scrub:1,       
    }
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
tl.from(".bg-flower-bottom-left ",{
    x:-200,
    opacity:0,
    stagger:0.2
})
tl.from(".bg-flower-bottom-right ",{
    x:200,
    opacity:0,
    stagger:0.2
})
