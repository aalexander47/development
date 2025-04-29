var tl=gsap.timeline()
tl.from(".floral-top ,.floral-top2 ",{
    y:-200,
    opacity:0,
})
tl.from(".title",{
    y:-200,
    opacity:0
})
tl.from(".invite",{
   scale:0.2,
    y:-400,
    opacity:0,
})

tl.from(".text ",{
    y:-200,
    opacity:0,
    scale:0.5,

})
tl.from(".date ",{
    y:-200,
    opacity:0,
    scale:0.5,
    duration:0.8
})
tl.from(".address ",{
    y:-200,
    opacity:0,
    scale:0.5,
    duration:0.8
})

tl.from(".footer",{
    y:-200,
    opacity:0,
    scale:0.5
})
tl.from(".floral-bottom",{
    x:-200,
    opacity:0,
    stagger:0.2
})
tl.from(".floral-bottom2 ",{
    x:200,
    opacity:0,
    stagger:0.2
})
