const fs = require('fs')


const words = [
  "apple",
  "places",
  "friends",
  "fructose",
  "pineapple",
  "jackhammer",
  "significant",
  "abandonments"
];

const scrabbleScores = {
  a: 1, b: 3, c: 3, d: 2, e: 1,
  f: 4, g: 2, h: 4, i: 1, j: 8,
  k: 5, l: 1, m: 3, n: 1, o: 1,
  p: 3, q: 10, r: 1, s: 1, t: 1,
  u: 1, v: 4, w: 4, x: 8, y: 4,
  z: 10
};

const getRandomWord = (wordList) => {
  const index = Math.floor(Math.random() * wordList.length);
  return wordList[index];
}


const topScoringLetter = (word) => {
  let topLetter = '';
  let topScore = 0;

  for (const letter of word.toLowerCase()) {
    const score = scrabbleScores[letter] || 0;
    if (score > topScore) {
      topScore = score;
      topLetter = letter;
    }
  }

  return topLetter;
}


const shuffle = (input) => {
	let word = input
	// substitute the top scoring letter
	const letter = topScoringLetter(word)
	const index = word.indexOf(letter);
	word = word.slice(0, index) + '?' + word.slice(index + 1);
	
	// reverse 50% of the time
	if (Math.random() < 0.5){
		word = word.split('').reverse().join('')
	}

	// shuffle
	const rIndex = Math.floor(Math.random() * (word.length + 1));
	word = word.slice(index + 1) + word.slice(0, index+1) 
	
	return word
}

const draw = (word) => {
	const shuffled = shuffle(word)
	const { createCanvas, loadImage } = require('canvas')
	const canvas = createCanvas(300, 300)
	const ctx = canvas.getContext('2d')

	const angle = 360 / shuffled.length

	// Write "Awesome!"
	ctx.font = '30px Impact'
	ctx.fillStyle = 'white';
	ctx.fillRect(0,0,300,300)

	ctx.fillStyle = 'black';
	let i = 0
	for (const letter of shuffled.split("")){
		const theta = i*angle * (Math.PI / 180);
		const distance = word.length * 10
		const x = Math.cos(theta) * distance;
	    const y = Math.sin(theta) * distance;
		ctx.fillText(letter, x + 150 , y + 150)
		i+=1
	}

	const out = fs.createWriteStream(`${word}.png`)
	const stream = canvas.createPNGStream()
	stream.pipe(out)
	out.on('finish', () =>  console.log('The PNG file was created.'))
}

for (const word of words){
	draw(word)
}
const word = shuffle(getRandomWord(words))


console.log('done')
