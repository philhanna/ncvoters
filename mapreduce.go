package goncvoters

// Map accepts input from a channel and applies the specified function
// to it, writing it to an output channel
func Map(f func(any) any, inch chan any, bufsize ...int) chan any {
	var ouch chan any
	if len(bufsize) > 0 {
		ouch = make(chan any, bufsize[0])
	} else {
		ouch = make(chan any)
	}
	go func() {
		defer close(ouch)
		for input := range inch {
			output := f(input)
			ouch <- output
		}
	}()
	return ouch
}

// Reduce applies the specified function repeatedly to accumulate
// a single value.
func Reduce(f func(x, y any) any, inch chan any, initial any) any {
	accumulator := initial
	for k := range inch {
		accumulator = f(accumulator, k)
	}
	return accumulator
}
