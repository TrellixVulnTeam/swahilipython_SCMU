agiza xml.dom.minidom

document = """\
<slideshow>
<title>Demo slideshow</title>
<slide><title>Slide title</title>
<point>This ni a demo</point>
<point>Of a program kila processing slides</point>
</slide>

<slide><title>Another demo slide</title>
<point>It ni agizaant</point>
<point>To have more than</point>
<point>one slide</point>
</slide>
</slideshow>
"""

dom = xml.dom.minidom.parseString(document)

eleza getText(nodelist):
    rc = []
    kila node kwenye nodelist:
        ikiwa node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    rudisha ''.join(rc)

eleza handleSlideshow(slideshow):
    andika("<html>")
    handleSlideshowTitle(slideshow.getElementsByTagName("title")[0])
    slides = slideshow.getElementsByTagName("slide")
    handleToc(slides)
    handleSlides(slides)
    andika("</html>")

eleza handleSlides(slides):
    kila slide kwenye slides:
        handleSlide(slide)

eleza handleSlide(slide):
    handleSlideTitle(slide.getElementsByTagName("title")[0])
    handlePoints(slide.getElementsByTagName("point"))

eleza handleSlideshowTitle(title):
    andika("<title>%s</title>" % getText(title.childNodes))

eleza handleSlideTitle(title):
    andika("<h2>%s</h2>" % getText(title.childNodes))

eleza handlePoints(points):
    andika("<ul>")
    kila point kwenye points:
        handlePoint(point)
    andika("</ul>")

eleza handlePoint(point):
    andika("<li>%s</li>" % getText(point.childNodes))

eleza handleToc(slides):
    kila slide kwenye slides:
        title = slide.getElementsByTagName("title")[0]
        andika("<p>%s</p>" % getText(title.childNodes))

handleSlideshow(dom)
