#encoding "utf-8"

InterestW -> "интерес" | "интересоваться";

InterestTitle -> (Word<gnc-agr[1]>) Word<gnc-agr[1]> ;

Interest -> InterestW InterestTitle interp (Interest.Name);
