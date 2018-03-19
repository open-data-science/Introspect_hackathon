#encoding "utf-8"

EduW -> "учиться" | "закончить";

EduNameNoun -> (Adj<gnc-agr[1]>) (Word<gnc-agr[1]>) Word<gnc-agr[1]> (Word<gnc-agr[1]>) (Word<gnc-agr[1]>) ;

Edu -> EduW EduNameNoun interp (Education.Name);

