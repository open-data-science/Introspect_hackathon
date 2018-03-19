#encoding "utf-8"

CourseW -> "курс" | "специализация";
CourseShort -> "к" | "спец";

CourseDescr -> CourseW | CourseShort;

CourseNameNoun -> (Adj<gnc-agr[1]>) (Word<gnc-agr[1]>) Word<gnc-agr[1], rt> (Word<gnc-agr[1]>) (Word<gnc-agr[1]>);

Course -> CourseDescr CourseNameNoun interp (Course.CourseName);

