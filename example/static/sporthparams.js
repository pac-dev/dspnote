let sporth;
const num = String.raw`(-?\d+(?:\.\d+)?)`;
const re = new RegExp(String.raw`_([\w]+) (\d+) palias ?# ?${num} - ${num},? ?${num}? ?\(?([\w]+)?\)?`, 'g');

function setP(i, p)
{
	if (typeof sporth.setp !== 'undefined') sporth.setp(i, p);
}

function createSlider(container, param, values)
{
	const paramDiv = document.createElement("div");
	paramDiv.className = "sliderOut";
	
	const label = document.createElement("div");
	label.innerHTML = param.name.replace(/_/g, ' ') + ":";
	label.className = "sliderLabel";
	paramDiv.appendChild(label);
	
	const slider = document.createElement("input");
	slider.type = "range";
	slider.min = param.min;
	slider.max = param.max;
	slider.step = (param.max - param.min) / 1000;
	slider.className = "sliderRange";
	paramDiv.appendChild(slider);
	
	const displ = document.createElement("div");
	displ.innerHTML = param.value + ' ' + param.units;
	displ.className = "sliderDispl";
	paramDiv.appendChild(displ);
	
	container.appendChild(paramDiv);
	
	slider.addEventListener('input', (event) => {
		values[param.name] = slider.value;
		setP(param.index, slider.value);
		displ.innerHTML = slider.value + ' ' + param.units;
	});
	
	slider.value = param.value;
	values[param.name] = slider.value;
}

export function createSliders(container, script, values = {})
{
	container.innerHTML = '';
	while(true) {
		const match = re.exec(script);
		if (!match) break;
		const param = {
			name: match[1],
			index: match[2],
			min: match[3],
			max: match[4],
		};
		if (values[param.name] !== undefined)
			param.value = values[param.name];
		else if (match[5] !== undefined)
			param.value = match[5];
		else
			param.value = param.min;
		param.units = (match[6] !== undefined) ? match[6] : '';
		createSlider(container, param, values);
	}
	return values;
}

export function setPvalues(script, values)
{
	while(true) {
		const match = re.exec(script);
		if (!match) break;
		const param = {
			name: match[1],
			index: match[2],
			min: match[3],
			max: match[4],
		};
		if (values[param.name] !== undefined)
			param.value = values[param.name];
		else if (match[5] !== undefined)
			param.value = match[5];
		else
			param.value = param.min;
		setP(param.index, param.value);
	}
}

export function init(sp)
{
	sporth = sp;
}
