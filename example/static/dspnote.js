import * as SporthDiagram from "./sporthdiagram.js";

window.addEventListener('load', function(){
	var figLock = {runningFig: null};
	SporthDiagram.createAll(document, figLock);
});

renderMathInElement(document.body, {delimiters: [
	{left: "$$", right: "$$", display: true},
	{left: "$", right: "$", display: false},
]});
