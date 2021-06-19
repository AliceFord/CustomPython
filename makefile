target: a.out
	./a.out

a.out: output.cpp
	g++ output/output.cpp

output.cpp:
	python3 main.py input/main.txt

clean:
	rm *.out