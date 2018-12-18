import * as SporthDiagram from "./sporthdiagram.js";
import * as ShaderFig from "./shaderfig.js";

window.addEventListener('load', function(){
	var figLock = {runningFig: null};
	SporthDiagram.createAll(document, figLock);
	ShaderFig.createAll(document, figLock);
});

renderMathInElement(document.body, {delimiters: [
	{left: "$$", right: "$$", display: true},
	{left: "$", right: "$", display: false},
]});
