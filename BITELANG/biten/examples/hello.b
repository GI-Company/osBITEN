cloudprint(HelloCloud);

cloudfunction mult(a, b) {
    cloudreturn a * b;
}

cloudvar x = 8;
cloudvar y = 11;
cloudprint(mult(x, y));