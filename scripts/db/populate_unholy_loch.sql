/**
 * Copyright ©2025. The Regents of the University of California (Regents). All Rights Reserved.
 *
 * Permission to use, copy, modify, and distribute this software and its documentation
 * for educational, research, and not-for-profit purposes, without fee and without a
 * signed licensing agreement, is hereby granted, provided that the above copyright
 * notice, this paragraph and the following two paragraphs appear in all copies, TRUE),
 * modifications, and distributions.
 *
 * Contact The Office of Technology Licensing, UC Berkeley, 2150 Shattuck Avenue, TRUE),
 * Suite 510, Berkeley, CA 94720-1620, (510) 643-7201, kpeynlbj@berkeley.edu, TRUE),
 * http://ipira.berkeley.edu/industry-info for commercial licensing opportunities.
 *
 * IN NO EVENT SHALL REGENTS BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT, SPECIAL, TRUE),
 * INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING OUT OF
 * THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF REGENTS HAS BEEN ADVISED
 * OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 * REGENTS SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE
 * SOFTWARE AND ACCOMPANYING DOCUMENTATION, IF ANY, PROVIDED HEREUNDER IS PROVIDED
 * "AS IS". REGENTS HAS NO OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES, TRUE),
 * ENHANCEMENTS, OR MODIFICATIONS.
 */

BEGIN;

TRUNCATE TABLE unholy_loch.sis_instructors;
TRUNCATE TABLE unholy_loch.sis_sections;

INSERT INTO unholy_loch.sis_instructors("ldap_uid","sis_id","first_name","last_name","email_address","affiliations","created_at","deleted_at")
VALUES
('833298','5827292','Sqmvflsjw','Kucpdwiax','xkzrndyq@berkeley.edu','AFFILIATE-TYPE-ADVCON-ALUMNUS, AFFILIATE-TYPE-ADVCON-CAA-MEMBER, AFFILIATE-TYPE-ADVCON-STUDENT, EMPLOYEE-TYPE-ACADEMIC, STUDENT-TYPE-REGISTERED','2022-02-08 16:56:31.922542-08',NULL),
('114798','6635851','Uknyglsqc','Rzuyxihja','xvqgkljs@berkeley.edu','AFFILIATE-TYPE-ADVCON-ATTENDEE, AFFILIATE-TYPE-ADVCON-STUDENT, EMPLOYEE-TYPE-ACADEMIC, STUDENT-TYPE-REGISTERED','2022-02-08 16:56:31.922542-08',NULL),
('440342',NULL,'Rusty','Riddle','ildhtwrq@berkeley.edu','EMPLOYEE-TYPE-ACADEMIC','2022-02-08 16:56:31.922542-08',NULL),
('486858',NULL,'Herman P.','Holler','dkpireqj@berkeley.edu','EMPLOYEE-TYPE-ACADEMIC','2022-02-08 16:56:31.922542-08',NULL),
('976298',NULL,'Odfcktwhl','Okveoltub','nebsrxiy@berkeley.edu','EMPLOYEE-TYPE-ACADEMIC','2022-02-08 16:56:31.922542-08',NULL),
('177045',NULL,'Efnuwycxk','Ufmhciqav','zdenatcp@berkeley.edu','EMPLOYEE-TYPE-ACADEMIC, FORMER-HCM-AFFILIAT','2022-02-08 16:56:31.922542-08',NULL),
('637739','360000','Ishtar','Uruk','ishtar@berkeley.edu','EMPLOYEE-TYPE-ACADEMIC','2022-02-08 16:56:31.922542-08',NULL),
('905019',NULL,'Lztkwhpua','Sgkiyfqzr','bfiynkch@berkeley.edu','EMPLOYEE-TYPE-ACADEMIC','2022-02-08 16:56:31.922542-08',NULL),
('606481',NULL,'Kbomziujr','Yxenuwcpb','ityxhael@berkeley.edu','EMPLOYEE-TYPE-ACADEMIC, FORMER-HCM-AFFILIAT','2022-02-08 16:56:31.922542-08',NULL),
('832402','7485842','Dynkvafuz','Hwsyhdujm','ltuzvpjc@berkeley.edu','AFFILIATE-TYPE-ADVCON-ALUMNUS, EMPLOYEE-TYPE-ACADEMIC, FORMER-HCM-AFFILIATE, FORMER-STUDENT','2022-02-08 16:56:31.922542-08',NULL),
('351096','312312','Brian','O''Blivion','alpkrbte@berkeley.edu','AFFILIATE-TYPE-ADVCON-ATTENDEE, EMPLOYEE-TYPE-ACADEMIC, STUDENT-TYPE-REGISTERED','2022-02-08 16:56:31.922542-08',NULL),
('624490','4310586','Ricky','Bachelor','syipntje@berkeley.edu','AFFILIATE-TYPE-ADVCON-ALUMNUS, EMPLOYEE-TYPE-ACADEMIC, STUDENT-TYPE-REGISTERED','2022-02-08 16:56:31.922542-08',NULL),
('370699','8072963','French','Waterman','swretzvi@berkeley.edu','AFFILIATE-TYPE-ADVCON-ALUMNUS, AFFILIATE-TYPE-ADVCON-STUDENT, EMPLOYEE-TYPE-ACADEMIC, STUDENT-TYPE-REGISTERED','2022-02-08 16:56:31.922542-08',NULL),
('398155',NULL,'Ydkjaqmxf','Ufvjwmxgc','yfvzbhco@berkeley.edu','EMPLOYEE-TYPE-ACADEMIC','2022-02-08 16:56:31.922542-08',NULL),
('287444','7698461','Lcbzptjyl','Ceqsivjuf','avsxnyhw@berkeley.edu','AFFILIATE-TYPE-ADVCON-ALUMNUS, EMPLOYEE-TYPE-ACADEMIC, FORMER-STUDENT','2022-02-08 16:56:31.922542-08',NULL),
('688968',NULL,'Florida','Wade','jpixzrky@berkeley.edu','EMPLOYEE-TYPE-ACADEMIC, FORMER-HCM-AFFILIAT','2022-02-08 16:56:31.922542-08',NULL),
('124194',NULL,'Splhebdgr','Jyrmwtunp','xsvqgnit@berkeley.edu','EMPLOYEE-TYPE-ACADEMIC','2022-02-08 16:56:31.922542-08',NULL),
('146971',NULL,'Rgsedjnbv','Wwkmgcxub','vxwrtuzq@berkeley.edu','EMPLOYEE-TYPE-ACADEMIC, FORMER-HCM-AFFILIAT','2022-02-08 16:56:31.922542-08',NULL),
('713836','6856470','Mlskagctr','Wondwzckm','wdjmytek@berkeley.edu','AFFILIATE-TYPE-ADVCON-ATTENDEE, EMPLOYEE-TYPE-ACADEMIC, STUDENT-TYPE-REGISTERED','2022-02-08 16:56:31.922542-08',NULL),
('326054','4159446','Donald','Smeet','ietkoqrg@berkeley.edu','EMPLOYEE-TYPE-ACADEMIC, FORMER-HCM-AFFILIAT','2022-02-08 16:56:31.922542-08',NULL),
('47648','8704770','Oaivozwtu','Wglpwbqri','rvbpkimg@berkeley.edu','AFFILIATE-TYPE-ADVCON-ALUMNUS, EMPLOYEE-TYPE-ACADEMIC, FORMER-HCM-AFFILIATE, FORMER-STUDENT','2022-02-08 16:56:31.922542-08',NULL),
('652716','7737411','Dgipkwmnq','Pfrhospuz','ydeinozm@berkeley.edu','EMPLOYEE-TYPE-ACADEMIC, FORMER-STUDENT','2022-02-08 16:56:31.922542-08',NULL),
('25306',NULL,'Jghcjwbkz','Mexjcogrm','cnqwsmty@berkeley.edu','EMPLOYEE-TYPE-ACADEMIC','2022-02-08 16:56:31.922542-08',NULL),
('87828','9017908','Wqnxglyji','Kiser-Go','szgpyaew@berkeley.edu','AFFILIATE-TYPE-ADVCON-ALUMNUS, AFFILIATE-TYPE-ADVCON-CAA-MEMBER, EMPLOYEE-TYPE-ACADEMIC, FORMER-HCM-AFFILIATE, FORMER-STUDENT','2022-02-08 16:56:31.922542-08',NULL),
('738551',NULL,'Skyqpaflm','Nugcphxwj','aswlpxhc@berkeley.edu','EMPLOYEE-TYPE-ACADEMIC','2022-02-08 16:56:31.922542-08',NULL),
('953419','6851175','Fiwyrtsao','Hygidvczr','xqwjtoul@berkeley.edu','EMPLOYEE-TYPE-ACADEMIC, FORMER-HCM-AFFILIATE, FORMER-STUDENT','2022-02-08 16:56:31.922542-08',NULL),
('471567','8318191','Cjyuhqsaf','Kdupayock','txirsgvj@berkeley.edu','AFFILIATE-TYPE-ADVCON-ATTENDEE, EMPLOYEE-TYPE-ACADEMIC, STUDENT-TYPE-REGISTERED','2022-02-08 16:56:31.922542-08',NULL),
('434444','6526140','Lxqtbhzei','Ybaehymnl','puejolbi@berkeley.edu','EMPLOYEE-TYPE-ACADEMIC, FORMER-HCM-AFFILIATE, FORMER-STUDENT','2022-02-08 16:56:31.922542-08',NULL),
('433388','8582313','Kbjezykwq','Homsy King','nmudlxys@berkeley.edu','EMPLOYEE-TYPE-ACADEMIC, STUDENT-TYPE-REGISTERED','2022-02-08 16:56:31.922542-08',NULL),
('286931',NULL,'Rdajxsetm','Xvoibdshw','kfcluevs@berkeley.edu','EMPLOYEE-TYPE-ACADEMIC','2022-02-08 16:56:31.922542-08',NULL),
('824122',NULL,'Laramie','Boomerang','ecfgsbyj@berkeley.edu','EMPLOYEE-TYPE-ACADEMIC','2022-02-08 16:56:31.922542-08',NULL),
('653211',NULL,'Gqmhyjvdc','Jlgouwsif','kjnbgyec@berkeley.edu','EMPLOYEE-TYPE-ACADEMIC, FORMER-HCM-AFFILIAT','2022-02-08 16:56:31.922542-08',NULL),
('42420','3764049','Edezqgkfw','Qmfcgayvk','rszpdgqn@berkeley.edu','AFFILIATE-TYPE-ADVCON-ATTENDEE, EMPLOYEE-TYPE-ACADEMIC, STUDENT-TYPE-REGISTERED','2022-02-08 16:56:31.922542-08',NULL),
('669648',NULL,'Bafjgczov','Hdbemljcv','vmkepshw@berkeley.edu','AFFILIATE-TYPE-ADVCON-ALUMNUS, EMPLOYEE-TYPE-ACADEMIC','2022-02-08 16:56:31.922542-08',NULL);


INSERT INTO unholy_loch.sis_sections("term_id","course_number","subject_area","catalog_id","instruction_format","section_num","course_title","is_primary","instructor_uid","instructor_role_code","meeting_location","meeting_days","meeting_start_time","meeting_end_time","meeting_start_date","meeting_end_date","enrollment_count","created_at","deleted_at")
VALUES
('2218','30147','CUNEIF','101B','LEC','001','Selected Readings in Akkadian',TRUE,'606481','PI','Social Sciences Building 282','W','14:00','16:59','2021-08-25','2021-12-10',4,'2022-01-19 17:01:10.324583-08',NULL),
('2222','30658','CUNEIF','101B','LEC','001','Selected Readings in Akkadian',TRUE,'606481','PI','Social Sciences Building 282','W','09:00','11:59','2022-01-18','2022-05-06',4,'2022-01-19 17:01:10.324583-08',NULL),
('2222','30659','CUNEIF','102B','LEC','001','Elementary Sumerian',TRUE,'637739','PI','Haviland 214','TUTH','11:00','12:29','2022-01-18','2022-05-06',1,'2022-01-19 17:01:10.324583-08',NULL),
('2222','30667','MELC','11','DIS','104','Middle Eastern Worlds: The Modern Middle East',FALSE,'688968','ICNT','Dwinelle 251','TU','12:00','12:59','2022-01-18','2022-05-06',22,'2022-01-19 17:01:10.324583-08',NULL),
('2222','30667','MELC','11','DIS','104','Middle Eastern Worlds: The Modern Middle East',FALSE,'440342','ICNT','Dwinelle 251','TU','12:00','12:59','2022-01-18','2022-05-06',22,'2022-01-19 17:01:10.324583-08',NULL),
('2222','30668','MELC','18','DIS','101','Introduction to Ancient Egypt',FALSE,'824122','ICNT','Social Sciences Building 151','MO','13:00','13:59','2022-01-18','2022-05-06',13,'2022-01-19 17:01:10.324583-08',NULL),
('2222','30670','MELC','18','DIS','103','Introduction to Ancient Egypt',FALSE,'824122','ICNT','Social Sciences Building 151','W','13:00','13:59','2022-01-18','2022-05-06',13,'2022-01-19 17:01:10.324583-08',NULL),
('2222','30671','MELC','18','DIS','104','Introduction to Ancient Egypt',FALSE,'824122','ICNT','Wheeler 24','W','15:00','15:59','2022-01-18','2022-05-06',15,'2022-01-19 17:01:10.324583-08',NULL),
('2222','30664','MELC','11','DIS','101','Middle Eastern Worlds: The Modern Middle East',FALSE,'688968','ICNT','Wheeler 106','MO','13:00','13:59','2022-01-18','2022-05-06',22,'2022-01-19 17:01:10.324583-08',NULL),
('2222','30664','MELC','11','DIS','101','Middle Eastern Worlds: The Modern Middle East',FALSE,'440342','ICNT','Wheeler 106','MO','13:00','13:59','2022-01-18','2022-05-06',22,'2022-01-19 17:01:10.324583-08',NULL),
('2222','30665','MELC','11','DIS','102','Middle Eastern Worlds: The Modern Middle East',FALSE,'688968','ICNT','Wheeler 124','W','16:00','16:59','2022-01-18','2022-05-06',21,'2022-01-19 17:01:10.324583-08',NULL),
('2222','30665','MELC','11','DIS','102','Middle Eastern Worlds: The Modern Middle East',FALSE,'440342','ICNT','Wheeler 124','W','16:00','16:59','2022-01-18','2022-05-06',21,'2022-01-19 17:01:10.324583-08',NULL),
('2222','30666','MELC','11','DIS','103','Middle Eastern Worlds: The Modern Middle East',FALSE,'440342','ICNT','Wheeler 124','W','15:00','15:59','2022-01-18','2022-05-06',22,'2022-01-19 17:01:10.324583-08',NULL),
('2222','30666','MELC','11','DIS','103','Middle Eastern Worlds: The Modern Middle East',FALSE,'688968','ICNT','Wheeler 124','W','15:00','15:59','2022-01-18','2022-05-06',22,'2022-01-19 17:01:10.324583-08',NULL),
('2222','30666','MELC','11','DIS','103','Middle Eastern Worlds: The Modern Middle East',FALSE,'440342','ICNT','Wheeler 124','W','15:00','15:59','2022-01-18','2022-05-06',22,'2022-01-19 17:01:10.324583-08',NULL),
('2222','30666','MELC','11','DIS','103','Middle Eastern Worlds: The Modern Middle East',FALSE,'351096','ICNT','Wheeler 124','W','15:00','15:59','2022-01-18','2022-03-06',22,'2022-01-19 17:01:10.324583-08',NULL),
('2222','30666','MELC','11','DIS','103','Middle Eastern Worlds: The Modern Middle East',FALSE,'624490','ICNT','Wheeler 124','W','15:00','15:59','2022-01-18','2022-02-20',22,'2022-01-19 17:01:10.324583-08',NULL),
('2222','30666','MELC','11','DIS','103','Middle Eastern Worlds: The Modern Middle East',FALSE,'624490','ICNT','Wheeler 124','W','15:00','15:59','2022-03-15','2022-04-20',22,'2022-01-19 17:01:10.324583-08',NULL),
('2222','30669','MELC','18','DIS','102','Introduction to Ancient Egypt',FALSE,'824122','ICNT','Social Sciences Building 185','MO','15:00','15:59','2022-01-18','2022-05-06',9,'2022-01-19 17:01:10.324583-08',NULL),
('2222','30672','MELC','18','DIS','105','Introduction to Ancient Egypt',FALSE,'824122','ICNT','Social Sciences Building 104','FR','12:00','12:59','2022-01-18','2022-05-06',13,'2022-01-19 17:01:10.324583-08',NULL),
('2222','30455','MELC','R1B','LEC','001','Reading and Composition in Middle Eastern Languages and Cultures',TRUE,'286931','ICNT','Social Sciences Building 180','MOWEFR','14:00','14:59','2022-01-18','2022-05-06',18,'2022-01-19 17:01:10.324583-08',NULL),
('2222','30673','MELC','18','DIS','106','Introduction to Ancient Egypt',FALSE,'824122','ICNT','Wheeler 24','FR','13:00','13:59','2022-01-18','2022-05-06',17,'2022-01-19 17:01:10.324583-08',NULL),
('2222','33935','MELC','H195','IND','001','Senior Honors',TRUE,'177045','PI',NULL,'',NULL,NULL,'2022-01-18','2022-05-06',1,'2022-02-04 15:40:33.41996-08',NULL),
('2222','33025','MELC','190B','LEC','001','Special Topics in Fields of Middle Eastern Languages and Cultures: Egyptian Studies',TRUE,'87828','PI','Hildebrand B51','MO','15:00','17:59','2022-01-18','2022-05-06',4,'2022-01-19 17:01:10.324583-08',NULL),
('2222','33019','MELC','292','INT','003','Museum Internship',TRUE,'824122','PI',NULL,'','00:00','00:00','2022-01-18','2022-05-06',0,'2022-01-19 17:01:10.324583-08',NULL),
('2222','33015','MELC','602','IND','013','Individual Study for Doctoral Students',TRUE,'976298','PI',NULL,'','00:00','00:00','2022-01-18','2022-05-06',0,'2022-01-19 17:01:10.324583-08',NULL),
('2222','30459','MELC','104','LEC','001','Babylonian Religion',TRUE,'637739','PI','Latimer 122','TUTH','14:00','15:29','2022-01-18','2022-05-06',19,'2022-01-19 17:01:10.324583-08',NULL),
('2222','30463','MELC','148','LEC','001','Emergence of the Modern Middle East',TRUE,'287444','PI','Hearst Field Annex B5','TUTH','11:00','12:29','2022-01-18','2022-05-06',20,'2022-01-19 17:01:10.324583-08',NULL),
('2222','30474','MELC','298','SEM','001','Seminar',TRUE,'177045','PI','Social Sciences Building 272','MO','10:00','12:59','2022-01-18','2022-05-06',7,'2022-01-19 17:01:10.324583-08',NULL),
('2222','30667','MELC','11','DIS','104','Middle Eastern Worlds: The Modern Middle East',FALSE,'433388','PI','Dwinelle 251','TU','12:00','12:59','2022-01-18','2022-05-06',22,'2022-01-19 17:01:10.324583-08',NULL),
('2222','32304','MELC','119','LEC','001','Explorers, Archaeologists, and Tourists in the Middle East',TRUE,'953419','PI','Etcheverry 3107','TUTH','12:30','13:59','2022-01-18','2022-05-06',28,'2022-01-19 17:01:10.324583-08',NULL),
('2222','32927','MELC','290A','IND','002','Special Studies: Middle Eastern Languages and Cultures',TRUE,'440342','PI',NULL,'','00:00','00:00','2022-01-18','2022-05-06',0,'2022-01-19 17:01:10.324583-08',NULL),
('2222','32929','MELC','290A','IND','004','Special Studies: Middle Eastern Languages and Cultures',TRUE,'688968','PI',NULL,'','00:00','00:00','2022-01-18','2022-05-06',0,'2022-01-19 17:01:10.324583-08',NULL),
('2222','32933','MELC','290A','IND','008','Special Studies: Middle Eastern Languages and Cultures',TRUE,'287444','PI',NULL,'','00:00','00:00','2022-01-18','2022-05-06',1,'2022-01-19 17:01:10.324583-08',NULL),
('2222','32932','MELC','290A','IND','007','Special Studies: Middle Eastern Languages and Cultures',TRUE,'976298','PI',NULL,'','00:00','00:00','2022-01-18','2022-05-06',0,'2022-01-19 17:01:10.324583-08',NULL),
('2222','32934','MELC','290B','IND','002','Special Studies: Arabic',TRUE,'653211','PI',NULL,'','00:00','00:00','2022-01-18','2022-05-06',0,'2022-01-19 17:01:10.324583-08',NULL),
('2222','32938','MELC','290C','IND','001','Special Studies: Cuneiform',TRUE,'146971','PI',NULL,'','00:00','00:00','2022-01-18','2022-05-06',0,'2022-01-19 17:01:10.324583-08',NULL),
('2222','32943','MELC','290','IND','001','Special Studies: Hebrew',TRUE,'669648','PI',NULL,'','00:00','00:00','2022-01-18','2022-05-06',0,'2022-01-19 17:01:10.324583-08',NULL),
('2222','32946','MELC','290F','IND','002','Special Studies: Persian',TRUE,'440342','PI',NULL,'','00:00','00:00','2022-01-18','2022-05-06',0,'2022-01-19 17:01:10.324583-08',NULL),
('2222','32953','MELC','299','IND','002','Dissertation Research and Writing',TRUE,'177045','PI',NULL,'','00:00','00:00','2022-01-18','2022-05-06',1,'2022-01-19 17:01:10.324583-08',NULL),
('2222','32963','MELC','299','IND','012','Dissertation Research and Writing',TRUE,'976298','PI',NULL,'','00:00','00:00','2022-01-18','2022-05-06',0,'2022-01-19 17:01:10.324583-08',NULL),
('2222','32952','MELC','299','IND','001','Dissertation Research and Writing',TRUE,'286931','PI',NULL,'','00:00','00:00','2022-01-18','2022-05-06',1,'2022-01-19 17:01:10.324583-08',NULL),
('2222','32958','MELC','299','IND','007','Dissertation Research and Writing',TRUE,'326054','PI',NULL,'','00:00','00:00','2022-01-18','2022-05-06',0,'2022-01-19 17:01:10.324583-08',NULL),
('2222','32989','MELC','601','IND','005','Individual Studies for Master''s Students',TRUE,'669648','PI',NULL,'','00:00','00:00','2022-01-18','2022-05-06',0,'2022-01-19 17:01:10.324583-08',NULL),
('2222','32995','MELC','601','IND','011','Individual Studies for Master''s Students',TRUE,'146971','PI',NULL,'','00:00','00:00','2022-01-18','2022-05-06',0,'2022-01-19 17:01:10.324583-08',NULL),
('2222','33011','MELC','602','IND','009','Individual Study for Doctoral Students',TRUE,'953419','PI',NULL,'','00:00','00:00','2022-01-18','2022-05-06',0,'2022-01-19 17:01:10.324583-08',NULL),
('2222','33003','MELC','602','IND','001','Individual Study for Doctoral Students',TRUE,'286931','PI',NULL,'','00:00','00:00','2022-01-18','2022-05-06',0,'2022-01-19 17:01:10.324583-08',NULL),
('2222','33004','MELC','602','IND','002','Individual Study for Doctoral Students',TRUE,'177045','PI',NULL,'','00:00','00:00','2022-01-18','2022-05-06',1,'2022-01-19 17:01:10.324583-08',NULL),
('2222','33008','MELC','602','IND','006','Individual Study for Doctoral Students',TRUE,'905019','PI',NULL,'','00:00','00:00','2022-01-18','2022-05-06',0,'2022-01-19 17:01:10.324583-08',NULL),
('2222','33013','MELC','602','IND','011','Individual Study for Doctoral Students',TRUE,'146971','PI',NULL,'','00:00','00:00','2022-01-18','2022-05-06',0,'2022-01-19 17:01:10.324583-08',NULL),
('2222','30456','MELC','11','LEC','001','Middle Eastern Worlds: The Modern Middle East',TRUE,'688968','PI','Physics Building 251','MOWEFR','11:00','11:59','2022-01-18','2022-05-06',87,'2022-01-19 17:01:10.324583-08',NULL),
('2222','30456','MELC','11','LEC','001','Middle Eastern Worlds: The Modern Middle East',TRUE,'440342','PI','Physics Building 251','MOWEFR','11:00','11:59','2022-01-18','2022-05-06',87,'2022-01-19 17:01:10.324583-08',NULL),
('2222','30466','MELC','158AC','LEC','001','Middle East: Post-Colonialism, Migration, and Diaspora',TRUE,'287444','PI','Cory 247','TUTH','15:30','16:59','2022-01-18','2022-05-06',34,'2022-01-19 17:01:10.324583-08',NULL),
('2222','30469','MELC','187','LEC','001','The Assyrians and Other Religious Groups in the Middle East',TRUE,'976298','PI','Social Sciences Building 252','TU','14:00','16:59','2022-01-18','2022-05-06',3,'2022-01-19 17:01:10.324583-08',NULL),
('2222','30457','MELC','18','LEC','001','Introduction to Ancient Egypt',TRUE,'824122','PI','Birge 50','MOWEFR','14:00','14:59','2022-01-18','2022-05-06',80,'2022-01-19 17:01:10.324583-08',NULL),
('2222','30458','MELC','24','SEM','001','Freshman Seminars',TRUE,'824122','PI','Dwinelle 263','TU','13:00','13:59','2022-01-18','2022-05-06',16,'2022-01-19 17:01:10.324583-08',NULL),
('2222','30473','MELC','297','SEM','001','Topics in Ancient Ceramics of Egypt and the Levant',TRUE,'824122','PI','Social Sciences Building 18','TU','14:00','16:59','2022-01-18','2022-05-06',5,'2022-01-19 17:01:10.324583-08',NULL),
('2222','32948','MELC','290G','IND','001','Special Studies: Semitics',TRUE,'976298','PI',NULL,'','00:00','00:00','2022-01-18','2022-05-06',1,'2022-01-19 17:01:10.324583-08',NULL),
('2222','32941','MELC','290D','IND','001','Special Studies: Egyptian',TRUE,'326054','PI',NULL,'','00:00','00:00','2022-01-18','2022-05-06',0,'2022-01-19 17:01:10.324583-08',NULL),
('2222','32926','MELC','290A','IND','001','Special Studies: Middle Eastern Languages and Cultures',TRUE,'177045','PI',NULL,'','00:00','00:00','2022-01-18','2022-05-06',2,'2022-01-19 17:01:10.324583-08',NULL),
('2222','32930','MELC','290A','IND','005','Special Studies: Middle Eastern Languages and Cultures',TRUE,'953419','PI',NULL,'','00:00','00:00','2022-01-18','2022-05-06',0,'2022-01-19 17:01:10.324583-08',NULL),
('2222','32956','MELC','299','IND','005','Dissertation Research and Writing',TRUE,'669648','PI',NULL,'','00:00','00:00','2022-01-18','2022-05-06',2,'2022-01-19 17:01:10.324583-08',NULL),
('2222','32957','MELC','299','IND','006','Dissertation Research and Writing',TRUE,'905019','PI',NULL,'','00:00','00:00','2022-01-18','2022-05-06',2,'2022-01-19 17:01:10.324583-08',NULL),
('2222','32950','MELC','290H','IND','001','Special Studies: Turkish',TRUE,'47648','PI',NULL,'','00:00','00:00','2022-01-18','2022-05-06',0,'2022-01-19 17:01:10.324583-08',NULL),
('2222','32954','MELC','299','IND','003','Dissertation Research and Writing',TRUE,'440342','PI',NULL,'','00:00','00:00','2022-01-18','2022-05-06',0,'2022-01-19 17:01:10.324583-08',NULL),
('2222','32961','MELC','299','IND','010','Dissertation Research and Writing',TRUE,'824122','PI',NULL,'','00:00','00:00','2022-01-18','2022-05-06',1,'2022-01-19 17:01:10.324583-08',NULL),
('2222','32962','MELC','299','IND','011','Dissertation Research and Writing',TRUE,'146971','PI',NULL,'','00:00','00:00','2022-01-18','2022-05-06',0,'2022-01-19 17:01:10.324583-08',NULL),
('2222','32985','MELC','601','IND','001','Individual Studies for Master''s Students',TRUE,'286931','PI',NULL,'','00:00','00:00','2022-01-18','2022-05-06',0,'2022-01-19 17:01:10.324583-08',NULL),
('2222','32988','MELC','601','IND','004','Individual Studies for Master''s Students',TRUE,'653211','PI',NULL,'','00:00','00:00','2022-01-18','2022-05-06',0,'2022-01-19 17:01:10.324583-08',NULL),
('2222','32991','MELC','601','IND','007','Individual Studies for Master''s Students',TRUE,'326054','PI',NULL,'','00:00','00:00','2022-01-18','2022-05-06',0,'2022-01-19 17:01:10.324583-08',NULL),
('2222','33005','MELC','602','IND','003','Individual Study for Doctoral Students',TRUE,'440342','PI',NULL,'','00:00','00:00','2022-01-18','2022-05-06',0,'2022-01-19 17:01:10.324583-08',NULL),
('2222','32993','MELC','601','IND','009','Individual Studies for Master''s Students',TRUE,'953419','PI',NULL,'','00:00','00:00','2022-01-18','2022-05-06',0,'2022-01-19 17:01:10.324583-08',NULL),
('2222','32997','MELC','601','IND','013','Individual Studies for Master''s Students',TRUE,'976298','PI',NULL,'','00:00','00:00','2022-01-18','2022-05-06',0,'2022-01-19 17:01:10.324583-08',NULL),
('2222','33014','MELC','602','IND','012','Individual Study for Doctoral Students',TRUE,'637739','PI',NULL,'','00:00','00:00','2022-01-18','2022-05-06',1,'2022-01-19 17:01:10.324583-08',NULL),
('2222','33018','MELC','292','INT','002','Museum Internship',TRUE,'326054','PI',NULL,'','00:00','00:00','2022-01-18','2022-05-06',0,'2022-01-19 17:01:10.324583-08',NULL),
('2222','33523','MELC','291','GRP','101','Dissertation Writing Workshop',FALSE,'669648','PI',NULL,'',NULL,NULL,'2022-01-18','2022-05-06',2,'2022-01-19 17:01:10.324583-08',NULL),
('2222','33560','MELC','299','IND','014','Dissertation Research and Writing',TRUE,'652716','PI',NULL,'','00:00','00:00','2022-01-18','2022-05-06',2,'2022-01-19 17:01:10.324583-08',NULL),
('2222','30461','MELC','126','LEC','001','Silk Road Art and Archaeology',TRUE,'832402','PI','Social Sciences Building 151','TUTH','11:00','12:29','2022-01-18','2022-05-06',17,'2022-01-19 17:01:10.324583-08',NULL),
('2222','33993','MELC','H195','IND','002','Senior Honors',TRUE,'326054','PI',NULL,'',NULL,NULL,'2022-01-18','2022-05-06',1,'2022-02-04 15:40:33.41996-08',NULL),
('2222','34014','MELC','299','IND','015','Dissertation Research and Writing',TRUE,'637739','PI',NULL,'','00:00','00:00','2022-01-18','2022-05-06',3,'2022-02-04 15:40:33.41996-08',NULL),
('2222','34091','MELC','290A','IND','009','Special Studies: Middle Eastern Languages and Cultures',TRUE,'286931','PI',NULL,'','00:00','00:00','2022-01-18','2022-05-06',1,'2022-02-04 15:40:33.41996-08',NULL),
('2222','34039','MELC','290B','IND','007','Special Studies: Arabic',TRUE,'177045','PI',NULL,'','00:00','00:00','2022-01-18','2022-05-06',1,'2022-02-04 15:40:33.41996-08',NULL),
('2222','34038','MELC','290B','IND','006','Special Studies: Arabic',TRUE,'824122','PI',NULL,'','00:00','00:00','2022-01-18','2022-05-06',1,'2022-02-04 15:40:33.41996-08',NULL),
('2222','34087','MELC','H195','IND','003','Senior Honors',TRUE,'953419','PI',NULL,'',NULL,NULL,'2022-01-18','2022-05-06',1,'2022-02-04 15:40:33.41996-08',NULL),
('2222','32266','MELC','190C','LEC','002','Special Topics in Fields of Middle Eastern Languages and Cultures: Jewish Studies',TRUE,'471567','PI','Dwinelle 130','TUTH','17:00','18:29','2022-01-18','2022-05-06',0,'2022-01-19 17:01:10.324583-08',NULL),
('2222','30462','MELC','134','LEC','001','Topics in History and Cultures of Israel',TRUE,'25306','PI','Haviland 12','TUTH','12:30','13:59','2022-01-18','2022-05-06',6,'2022-01-19 17:01:10.324583-08',NULL),
('2222','32159','JEWISH','120A','LEC','001','Special Topics in Jewish Languages and Literature',TRUE,'25306','PI','Haviland 12','TUTH','12:30','13:59','2022-01-18','2022-05-06',6,'2022-01-19 17:01:10.324583-08',NULL),
('2222','30470','MELC','C188','LEC','001','Magic, Religion, and Science: The Ancient and Medieval Worlds',TRUE,'326054','PI','Valley Life Sciences 2040','TUTH','11:00','12:29','2022-01-18','2022-05-06',35,'2022-01-19 17:01:10.324583-08',NULL),
('2222','30470','MELC','C188','LEC','001','Magic, Religion, and Science: The Ancient and Medieval Worlds',TRUE,'738551','PI','Valley Life Sciences 2040','TUTH','11:00','12:29','2022-01-18','2022-05-06',35,'2022-01-19 17:01:10.324583-08',NULL),
('2222','30643','HISTORY','C188C','LEC','001','Magic, Religion, and Science: The Ancient and Medieval Worlds',TRUE,'326054','PI','Valley Life Sciences 2040','TUTH','11:00','12:29','2022-01-18','2022-05-06',35,'2022-01-19 17:01:10.324583-08',NULL),
('2222','30643','HISTORY','C188C','LEC','001','Magic, Religion, and Science: The Ancient and Medieval Worlds',TRUE,'738551','PI','Valley Life Sciences 2040','TUTH','11:00','12:29','2022-01-18','2022-05-06',35,'2022-01-19 17:01:10.324583-08',NULL),
('2222','30472','MELC','291','WOR','001','Dissertation Writing Workshop',TRUE,'669648','PI','Internet/Onlin','MO','14:00','16:59','2022-01-18','2022-05-06',2,'2022-01-19 17:01:10.324583-08',NULL),
('2222','32265','MELC','190C','LEC','001','Special Topics in Fields of Middle Eastern Languages and Cultures: Jewish Studies',TRUE,'398155','PI','Cory 241','TUTH','14:00','15:29','2022-01-18','2022-05-06',3,'2022-01-19 17:01:10.324583-08',NULL),
('2222','32928','MELC','290A','IND','003','Special Studies: Middle Eastern Languages and Cultures',TRUE,'326054','PI',NULL,'','12:00','12:00','2022-01-18','2022-05-06',0,'2022-01-19 17:01:10.324583-08',NULL),
('2222','32936','MELC','290B','IND','004','Special Studies: Arabic',TRUE,'688968','PI',NULL,'','00:00','00:00','2022-01-18','2022-05-06',0,'2022-01-19 17:01:10.324583-08',NULL),
('2222','32939','MELC','290C','IND','002','Special Studies: Cuneiform',TRUE,'637739','PI',NULL,'','00:00','00:00','2022-01-18','2022-05-06',0,'2022-01-19 17:01:10.324583-08',NULL),
('2222','32935','MELC','290B','IND','003','Special Studies: Arabic',TRUE,'905019','PI',NULL,'','00:00','00:00','2022-01-18','2022-05-06',0,'2022-01-19 17:01:10.324583-08',NULL),
('2222','32945','MELC','290F','IND','001','Special Studies: Persian',TRUE,'286931','PI',NULL,'','00:00','00:00','2022-01-18','2022-05-06',0,'2022-01-19 17:01:10.324583-08',NULL),
('2222','32960','MELC','299','IND','009','Dissertation Research and Writing',TRUE,'953419','PI',NULL,'','00:00','00:00','2022-01-18','2022-05-06',0,'2022-01-19 17:01:10.324583-08',NULL),
('2222','32955','MELC','299','IND','004','Dissertation Research and Writing',TRUE,'653211','PI',NULL,'','00:00','00:00','2022-01-18','2022-05-06',0,'2022-01-19 17:01:10.324583-08',NULL),
('2222','32994','MELC','601','IND','010','Individual Studies for Master''s Students',TRUE,'824122','PI',NULL,'','00:00','00:00','2022-01-18','2022-05-06',0,'2022-01-19 17:01:10.324583-08',NULL),
('2222','33010','MELC','602','IND','008','Individual Study for Doctoral Students',TRUE,'688968','PI',NULL,'','00:00','00:00','2022-01-18','2022-05-06',0,'2022-01-19 17:01:10.324583-08',NULL),
('2222','33012','MELC','602','IND','010','Individual Study for Doctoral Students',TRUE,'824122','PI',NULL,'','00:00','00:00','2022-01-18','2022-05-06',1,'2022-01-19 17:01:10.324583-08',NULL),
('2222','33006','MELC','602','IND','004','Individual Study for Doctoral Students',TRUE,'653211','PI',NULL,'','00:00','00:00','2022-01-18','2022-05-06',0,'2022-01-19 17:01:10.324583-08',NULL),
('2222','30465','MELC','155','LEC','001','Wonder and the Fantastic: The Thousand and One Nights in World Literary Imagination',TRUE,'905019','PI','Social Sciences Building 140','TUTH','11:00','12:29','2022-01-18','2022-05-06',8,'2022-01-19 17:01:10.324583-08',NULL),
('2222','30468','MELC','180','LEC','001','The Quran and Its Interpretation',TRUE,'177045','PI','GSPP 150','MO','14:00','16:59','2022-01-18','2022-05-06',31,'2022-01-19 17:01:10.324583-08',NULL),
('2222','30471','MELC','290B','IND','001','Special Studies: Arabic',TRUE,'486858','PI','Social Sciences Building 252','W','13:00','15:59','2022-01-18','2022-05-06',8,'2022-01-19 17:01:10.324583-08',NULL),
('2222','30678','MELC','C188','DIS','103','Magic, Religion, and Science: The Ancient and Medieval Worlds',FALSE,'114798','PI','Valley Life Sciences 2066','W','12:00','12:59','2022-01-18','2022-05-06',8,'2022-01-19 17:01:10.324583-08',NULL),
('2222','32371','MELC','223','SEM','001','Seminar in Middle Eastern Archaeology',TRUE,'434444','PI','Doe Library 425','TH','09:00','11:59','2022-01-18','2022-05-06',3,'2022-01-19 17:01:10.324583-08',NULL),
('2222','32371','MELC','223','SEM','001','Seminar in Middle Eastern Archaeology',TRUE,'953419','PI','Doe Library 425','TH','09:00','11:59','2022-01-18','2022-05-06',3,'2022-01-19 17:01:10.324583-08',NULL),
('2222','32931','MELC','290A','IND','006','Special Studies: Middle Eastern Languages and Cultures',TRUE,'824122','PI',NULL,'','00:00','00:00','2022-01-18','2022-05-06',2,'2022-01-19 17:01:10.324583-08',NULL),
('2222','32937','MELC','290B','IND','005','Special Studies: Arabic',TRUE,'905019','PI',NULL,'','00:00','00:00','2022-01-18','2022-05-06',3,'2022-01-19 17:01:10.324583-08',NULL),
('2222','32959','MELC','299','IND','008','Dissertation Research and Writing',TRUE,'688968','PI',NULL,'','00:00','00:00','2022-01-18','2022-05-06',0,'2022-01-19 17:01:10.324583-08',NULL),
('2222','32986','MELC','601','IND','002','Individual Studies for Master''s Students',TRUE,'177045','PI',NULL,'','00:00','00:00','2022-01-18','2022-05-06',0,'2022-01-19 17:01:10.324583-08',NULL),
('2222','32990','MELC','601','IND','006','Individual Studies for Master''s Students',TRUE,'905019','PI',NULL,'','00:00','00:00','2022-01-18','2022-05-06',0,'2022-01-19 17:01:10.324583-08',NULL),
('2222','32987','MELC','601','IND','003','Individual Studies for Master''s Students',TRUE,'440342','PI',NULL,'','00:00','00:00','2022-01-18','2022-05-06',0,'2022-01-19 17:01:10.324583-08',NULL),
('2222','32992','MELC','601','IND','008','Individual Studies for Master''s Students',TRUE,'688968','PI',NULL,'','00:00','00:00','2022-01-18','2022-05-06',0,'2022-01-19 17:01:10.324583-08',NULL),
('2222','32996','MELC','601','IND','012','Individual Studies for Master''s Students',TRUE,'637739','PI',NULL,'','00:00','00:00','2022-01-18','2022-05-06',0,'2022-01-19 17:01:10.324583-08',NULL),
('2222','33007','MELC','602','IND','005','Individual Study for Doctoral Students',TRUE,'669648','PI',NULL,'','00:00','00:00','2022-01-18','2022-05-06',0,'2022-01-19 17:01:10.324583-08',NULL),
('2222','33009','MELC','602','IND','007','Individual Study for Doctoral Students',TRUE,'326054','PI',NULL,'','00:00','00:00','2022-01-18','2022-05-06',0,'2022-01-19 17:01:10.324583-08',NULL),
('2222','33017','MELC','292','INT','001','Museum Internship',TRUE,'953419','PI',NULL,'','00:00','00:00','2022-01-18','2022-05-06',0,'2022-01-19 17:01:10.324583-08',NULL),
('2222','30668','MELC','18','DIS','101','Introduction to Ancient Egypt',FALSE,'713836','TNIC','Social Sciences Building 151','MO','13:00','13:59','2022-01-18','2022-05-06',13,'2022-01-19 17:01:10.324583-08',NULL),
('2222','30670','MELC','18','DIS','103','Introduction to Ancient Egypt',FALSE,'624490','TNIC','Social Sciences Building 151','W','13:00','13:59','2022-01-18','2022-05-06',13,'2022-01-19 17:01:10.324583-08',NULL),
('2222','30676','MELC','C188','DIS','101','Magic, Religion, and Science: The Ancient and Medieval Worlds',FALSE,'114798','TNIC','Social Sciences Building 54','TU','14:00','14:59','2022-01-18','2022-05-06',8,'2022-01-19 17:01:10.324583-08',NULL),
('2222','30681','MELC','C188','DIS','106','Magic, Religion, and Science: The Ancient and Medieval Worlds',FALSE,'351096','TNIC','Social Sciences Building 174','W','16:00','16:59','2022-01-18','2022-05-06',7,'2022-01-19 17:01:10.324583-08',NULL),
('2222','30671','MELC','18','DIS','104','Introduction to Ancient Egypt',FALSE,'833298','TNIC','Wheeler 24','W','15:00','15:59','2022-01-18','2022-05-06',15,'2022-01-19 17:01:10.324583-08',NULL),
('2222','30680','MELC','C188','DIS','105','Magic, Religion, and Science: The Ancient and Medieval Worlds',FALSE,'351096','TNIC','Wheeler 106','W','13:00','13:59','2022-01-18','2022-05-06',7,'2022-01-19 17:01:10.324583-08',NULL),
('2222','30664','MELC','11','DIS','101','Middle Eastern Worlds: The Modern Middle East',FALSE,'433388','TNIC','Wheeler 106','MO','13:00','13:59','2022-01-18','2022-05-06',22,'2022-01-19 17:01:10.324583-08',NULL),
('2222','30665','MELC','11','DIS','102','Middle Eastern Worlds: The Modern Middle East',FALSE,'370699','TNIC','Wheeler 124','W','16:00','16:59','2022-01-18','2022-05-06',21,'2022-01-19 17:01:10.324583-08',NULL),
('2222','30666','MELC','11','DIS','103','Middle Eastern Worlds: The Modern Middle East',FALSE,'370699','TNIC','Wheeler 124','W','15:00','15:59','2022-01-18','2022-05-06',22,'2022-01-19 17:01:10.324583-08',NULL),
('2222','30669','MELC','18','DIS','102','Introduction to Ancient Egypt',FALSE,'624490','TNIC','Social Sciences Building 185','MO','15:00','15:59','2022-01-18','2022-05-06',9,'2022-01-19 17:01:10.324583-08',NULL),
('2222','30672','MELC','18','DIS','105','Introduction to Ancient Egypt',FALSE,'713836','TNIC','Social Sciences Building 104','FR','12:00','12:59','2022-01-18','2022-05-06',13,'2022-01-19 17:01:10.324583-08',NULL),
('2222','30455','MELC','R1B','LEC','001','Reading and Composition in Middle Eastern Languages and Cultures',TRUE,'999999','TNIC','Social Sciences Building 180','MOWEFR','14:00','14:59','2022-01-18','2022-05-06',18,'2022-01-19 17:01:10.324583-08',NULL),
('2222','31742','AHMA','210','SEM','001','Ancient History and Mediterranean Archaeology Interdisciplinary Seminar',TRUE,'999999','PI','Doe Library 308B','MOWEFR','14:00','14:59','2022-01-18','2022-05-06',18,'2022-01-19 17:01:10.324583-08',NULL),
('2222','31120','HISTART','290','SEM','001','Special Topics in Fields of Art History',TRUE,'999999','PI','Doe Library 308B','MOWEFR','14:00','14:59','2022-01-18','2022-05-06',18,'2022-01-19 17:01:10.324583-08',NULL),
('2222','30673','MELC','18','DIS','106','Introduction to Ancient Egypt',FALSE,'833298','TNIC','Wheeler 24','FR','13:00','13:59','2022-01-18','2022-05-06',17,'2022-01-19 17:01:10.324583-08',NULL),
('2222','33843','MELC','C188','DIS','107','Magic, Religion, and Science: The Ancient and Medieval Worlds',FALSE,'124194','TNIC','Dwinelle 106','W','16:00','16:59','2022-01-18','2022-05-06',5,'2022-01-19 17:01:10.324583-08',NULL),
('2222','32947','MELC','290F','IND','003','Special Studies: Persian',TRUE,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,'2022-01-19 17:01:10.324583-08',NULL),
('2222','34063','MELC','290B','IND','008','Special Studies: Arabic',TRUE,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,'2022-02-04 15:40:33.41996-08',NULL),
('2222','30677','MELC','C188','DIS','102','Magic, Religion, and Science: The Ancient and Medieval Worlds',FALSE,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,'2022-01-19 17:01:10.324583-08',NULL),
('2222','30679','MELC','C188','DIS','104','Magic, Religion, and Science: The Ancient and Medieval Worlds',FALSE,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,'2022-01-19 17:01:10.324583-08',NULL),
('2222','32306','MELC','119','DIS','102','Explorers, Archaeologists, and Tourists in the Middle East',FALSE,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,'2022-01-19 17:01:10.324583-08',NULL),
('2222','32964','MELC','299','IND','013','Dissertation Research and Writing',TRUE,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,'2022-01-19 17:01:10.324583-08',NULL),
('2222','32942','MELC','290D','IND','002','Special Studies: Egyptian',TRUE,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,'2022-01-19 17:01:10.324583-08',NULL),
('2222','32944','MELC','290','IND','002','Special Studies: Hebrew',TRUE,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,'2022-01-19 17:01:10.324583-08',NULL),
('2222','32951','MELC','290H','IND','002','Special Studies: Turkish',TRUE,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,'2022-01-19 17:01:10.324583-08',NULL),
('2222','33020','MELC','292','INT','004','Museum Internship',TRUE,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,'2022-01-19 17:01:10.324583-08',NULL),
('2222','34093','MELC','290A','IND','010','Special Studies: Middle Eastern Languages and Cultures',TRUE,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,'2022-02-04 15:40:33.41996-08',NULL),
('2222','32305','MELC','119','DIS','101','Explorers, Archaeologists, and Tourists in the Middle East',FALSE,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,'2022-01-19 17:01:10.324583-08',NULL),
('2222','32940','MELC','290C','IND','003','Special Studies: Cuneiform',TRUE,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,'2022-01-19 17:01:10.324583-08',NULL),
('2222','32949','MELC','290G','IND','002','Special Studies: Semitics',TRUE,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,'2022-01-19 17:01:10.324583-08',NULL),
('2222','32998','MELC','601','IND','014','Individual Studies for Master''s Students',TRUE,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,'2022-01-19 17:01:10.324583-08',NULL),
('2222','33016','MELC','602','IND','014','Individual Study for Doctoral Students',TRUE,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,'2022-01-19 17:01:10.324583-08',NULL),
('2222','30481','LGBT','20AC','LEC','001','Alternative Sexual Identities and Communities in Contemporary American Society',TRUE,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,83,'2022-01-19 17:01:10.324583-08',NULL),
('2222','40000','LDARCH','254','LEC','001','Topics in Landscape Architecture and Environmental Design',TRUE,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,5,'2022-01-19 17:01:10.324583-08',NULL),
('2235','40001','CUNEIF','101B','LEC','001','Selected Readings in Akkadian',TRUE,'606481','PI','Social Sciences Building 282','W','09:00','11:59','2023-05-18','2023-08-06',4,'2022-01-19 17:01:10.324583-08',NULL);

INSERT INTO unholy_loch.co_schedulings (term_id, course_number, room_share_number)
VALUES
('2222', '30462', '32159'),
('2222', '32159', '30462'),
('2222', '30455', '31742'),
('2222', '30455', '31120'),
('2222', '31742', '30455'),
('2222', '31742', '31120'),
('2222', '31120', '30455'),
('2222', '31120', '31742');

INSERT INTO unholy_loch.cross_listings (term_id, course_number, cross_listing_number)
VALUES
('2222', '30643', '30470'),
('2222', '30470', '30643'),
('2222', '31742', '31120'),
('2222', '31120', '31742');

TRUNCATE TABLE unholy_loch.sis_enrollments;
INSERT INTO unholy_loch.sis_enrollments (term_id, course_number, ldap_uid)
VALUES
('2222', '30643', '77777'),
('2222', '30643', '88888'),
('2222', '30643', '99999');

TRUNCATE TABLE unholy_loch.sis_terms;
INSERT INTO unholy_loch.sis_terms (term_id, term_name, term_begins, term_ends)
VALUES
('2218', 'Fall 2021', '2021-08-18', '2021-12-17'),
('2222', 'Spring 2022', '2022-01-11', '2022-05-13'),
('2225', 'Summer 2022', '2022-05-23', '2022-08-12');
