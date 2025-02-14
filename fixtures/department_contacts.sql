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
 * Suite 510, Berkeley, CA 94720-1620, (510) 643-7201, otl@berkeley.edu, TRUE),
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

TRUNCATE TABLE department_members;
DELETE FROM users WHERE NOT is_admin;

INSERT INTO users (uid, csid, first_name, last_name, email, is_admin, blue_permissions, created_at, updated_at, deleted_at) VALUES
('100','100100100','Father','Brennan','fatherbrennan@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('300','300300300','Robert','Thorn','rt@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('400','400400500','Kathy','Thorn','kt@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('500',NULL, 'Keith','Jennings','kj@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('6555809','606614789','Gupter','Diederley','gupter.diederley@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('8432154','366020422','Hurdley','Bardolf','hurdley.bardolf@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('9115040','209239434','Bebe','de la Rosa','bebe@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('1007025','237003576','Tank','Spitz','tank.spitz@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('7464420','650928736','Colin','O''Brother','colin.obrother@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('6736735',NULL,'Roland','Bestwestern','roland.bestwestern@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('9994739','235826537','Chevy','Mcgee','chevy.mcgee@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('5009639','188191561','Ansel','Manchester','ansel.manchester@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('649411','856329057','Henderson','Ross','henderson.ross@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('3144822','422751601','Chat','Dibbins','chat.dibbins@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('231932','308895614','Geert','Biederschmitz','geert.biederschmitz@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('6355075','61287218','Morys','Whyte','morys.whyte@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('5735619','293342950','Eugina','Lang','eugina.lang@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('4633582','287612280','Bentley','Blackberry','bentley.blackberry@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('5007271',NULL,'Hugh','Dispenser','hugh.dispenser@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('5006125','853754993','Seeley','Brunk','seeley.brunk@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('6713140','683074453','Gutzon','Borglum','gutzon.borglum@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('6421446','464429561','Syd','Ziegler','syd.ziegler@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('8971283','294078726','Finn','Wolfhard','finn.wolfhard@berkeley.edu',FALSE,'reports_only',now(),now(),NULL),
('5013530','931203945','Jazz','Gunn','jazz.gunn@berkeley.edu',FALSE,'response_rates',now(),now(),NULL),
('6982398','263809005','Alistair','Mctaggert','alistair.mctaggert@berkeley.edu',FALSE,'reports_only',now(),now(),NULL),
('6447649','821991770','Jimmy','Integer','jimmy.integer@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('8695812','555362226','Dolby','Sprout','dolby.sprout@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('9924360','558442463','Kelli','Montecristo','kelli.montecristo@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('6064376','406165658','Clementine','Paddleford','clementine.paddleford@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('7511274','608626569','Gordy','Boytana','gordy.boytana@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('7498395','750348517','Dake','Traphagen','dake.traphagen@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('2111285','464793128','Tinsley','Gallian','tinsley.gallian@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('682608','26909666','Connie','Mcgerk','connie.mcgerk@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('169465','409123739','Chet','Bergersen','chet.bergersen@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('8611177','413381130','Bobby-Drake','Keith','bobby-drake.keith@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('2561505','122450495','Bubba','Bean','bubba.bean@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('9144257','677145485','Preston','Dixon','preston.dixon@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('7668314',NULL,'Bradrick','O''Broderick','brad@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('5357973','781881836','Manny','Laboy','manny.laboy@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('1079197','240628770','Stetson','Ryder','stetson.ryder@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('730770','293808039','Golden','Romney','golden.romney@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('1416250','241860811','Maverick','Hawk','maverick.hawk@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('2097533','891793945','Shad','Rowdy','shad.rowdy@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('9452902','384061945','Crain','Bundulance','crain.bundulance@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('1154327','517215519','Calbert','Buggs','calbert.buggs@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('1808566','166270364','Tilli','Sinterklaas','tilli.sinterklaas@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('5987999','164303071','Brint','Mckinsley','brint.mckinsley@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('3119357','471944673','Paul','Hallelujah','paul.hallelujah@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('1044514','195509517','Dave','O''Zone','dave.ozone@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('4573100','182938354','Brian','O''Blivion','brian@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('2577027','45160135','Barry','Convex','barry.convex@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('8197848','167315615','Ricky','Bachelor','ricky.bachelor@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('6900324','896337985','Kris','Tingler','kris.tingler@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('7230846','19821206','Hollywood','Cantrell','hollywood.cantrell@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('7723961','882439887','Tevin','Maddox','tevin.maddox@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('3474284','233188781','Bobo','Huffnagel','bobo.huffnagel@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('2975818','780164674','Sandy','Peacock','sandy.peacock@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('3751664','465221434','Bobby','Mumper','b.m@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('9424941','646578175','Tanner','Arborgast','tanner.arborgast@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('5001672','435147302','Dorson','Trotter','dorson.trotter@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('8163458','430892178','Delbert','Rhodes','delbert.rhodes@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('8034029','401180566','Channon','Hatcher','channon.hatcher@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('5738750','940591071','Brody','Swink','brody.swink@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('1253868','988634755','Slade','Tomberlane','slade.tomberlane@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('4097373',NULL,'Third','Heighter','third.heighter@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('8449142','805282349','Berklee','Pear','berklee.pear@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('9200664','212063640','Cj','Slugantz','cj.slugantz@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('5001974','636220395','Scarlet','Polaris','scarlet.polaris@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('9419442','39566708','Klaus','Bidet','klaus.bidet@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('5000241','639014843','Chandler','Platt','chandler.platt@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('5003541','780000430','Korb','Sanjay','korb.sanjay@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('2077852','572521067','Skip','Franzen','skip.franzen@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('500382',NULL,'Rusty','Goins','rusty.goins@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('5000419','252890992','Murphy','Damron','murphy.damron@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('8419802','56967092','Algernon','Chalifoux','algernon.chalifoux@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('1246825','393447210','Art','Would','art.would@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('225628','621365292','Joaquin','Away','joaquin.away@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('4119684','904418907','Skip','Brevity','skip.brevity@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('7734960','683656403','Warfield','Donahue','warfield.donahue@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('5291686','709420944','Linville','Pocket','linville.pocket@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('6712098','469484846','Norbert','Rubb','norber.rubb@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('7736123','486629959','Carol','Merrell','carol.merrell@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('5562743','918665106','Jolene','Strawberry-Fields','jolene.strawberry-fields@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('8112725','793931630','Phineas','Lair','phineas.lair@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('5096541','869006730','Charles','Clever','charles.clever@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('1261335','449221321','Kermit','Waldo','kermit.waldo@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('3213874','250435493','Skeeter','Skelton','skeeter.skelton@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('13562','58801255','Meredith','Marmaduke','meredith.marmaduke@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('1689443','287958844','Wendell','Eggbert','wendell.eggbert@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('139468','119929260','Rand','Anderson','rand.anderson@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('2570154','96406975','Desiderius','Erasmus','desiderius.erasmus@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('5009424','271806385','House','Rockwell','house.rockwell@berkeley.edu',FALSE,NULL,now(),now(),now()),
('611072','895363514','Shatina','Sheets','shatina.sheets@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('1374470','136913290','Blexandra','Wong','blexandra.wong@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('5035229','684360603','Kristian','Flagg','kristian.flagg@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('1769559',NULL,'Sandy','Hans','sandy.hans@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('198326',NULL,'Prince','Raspberry','prince.raspberry@berkeley.edu',FALSE,NULL,now(),now(),NULL),
('1042209','985171781','Dagatha','M''Lady','d@berkeley.edu',FALSE,NULL,now(),now(),NULL);

CREATE TEMP TABLE dept_uids (dept_name VARCHAR, uid VARCHAR, can_receive_communications BOOLEAN);
INSERT INTO dept_uids VALUES
('Engineering','6555809',TRUE),
('Engineering','8432154',TRUE),
('Engineering','9115040',TRUE),
('Middle Eastern Languages and Cultures','1007025',TRUE),
('Legal Studies','7464420',TRUE),
('Industrial Engineering and Operations Research','6736735',TRUE),
('Bioengineering','6555809',TRUE),
('Bioengineering','8432154',TRUE),
('Information','649411',TRUE),
('Information','3144822',TRUE),
('Global Metropolitan Studies','6355075',TRUE),
('Linguistics','5735619',TRUE),
('Computing, Data Science, and Society','4633582',TRUE),
('Public Health','9997271',TRUE),
('Astronomy','2306125',TRUE),
('Theater, Dance and Performance Studies','6713140',TRUE),
('Anthropology','6421446',TRUE),
('Film and Media','8971283',TRUE),
('Integrative Biology','5013530',TRUE),
('Integrative Biology','6982398',TRUE),
('Civil and Environmental Engineering','6447649',TRUE),
('Mathematics','6555809',TRUE),
('Mathematics','9924360',TRUE),
('Agricultural and Resource Economics','6064376',TRUE),
('Helen Wills Neuroscience','7511274',TRUE),
('Art Practice','7498395',TRUE),
('Italian Studies','2111285',TRUE),
('Physics','682608',TRUE),
('Slavic Languages and Literatures','169465',TRUE),
('Electrical Engineering and Computer Sciences','6555809',TRUE),
('Electrical Engineering and Computer Sciences','2561505',TRUE),
('Electrical Engineering and Computer Sciences','9144257',TRUE),
('Rhetoric','7668314',TRUE),
('Materials Science and Engineering','5357973',TRUE),
('African American Studies','1079197',TRUE),
('African American Studies','730770',TRUE),
('Nutritional Sciences and Toxicology','1416250',TRUE),
('Architecture','2097533',TRUE),
('Demography','9452902',TRUE),
('Environmental Science, Policy and Management','1154327',TRUE),
('Environmental Science, Policy and Management','1808566',TRUE),
('Scandinavian','5987999',TRUE),
('Comparative Literature','3119357',TRUE),
('Military Affairs','1044514',TRUE),
('Plant and Microbial Biology','4573100',TRUE),
('Ancient Greek and Roman Studies','2577027',TRUE),
('Ancient Greek and Roman Studies','8197848',TRUE),
('Mechanical Engineering','6900324',TRUE),
('Statistics','7230846',TRUE),
('Statistics','7723961',TRUE),
('English','3474284',TRUE),
('New Media','2975818',TRUE),
('Economics','3751664',TRUE),
('History of Art','9424941',TRUE),
('History','3681672',TRUE),
('History','8163458',TRUE),
('Spanish and Portuguese','8034029',TRUE),
('Spanish and Portuguese','5738750',TRUE),
('German','1253868',TRUE),
('CalTeach','4097373',TRUE),
('CalTeach','8449142',TRUE),
('CalTeach','9200664',TRUE),
('Molecular and Cell Biology','8621974',TRUE),
('Chemical and Biomolecular Engineering','9419442',TRUE),
('Chemistry','6363505',TRUE),
('Chemistry','3863541',TRUE),
('International and Area Studies','2077852',TRUE),
('Geography','434382',TRUE),
('Celtic Studies','1290419',TRUE),
('Social Welfare','8419802',TRUE),
('Undergraduate and Interdisciplinary Studies','1246825',TRUE),
('Earth and Planetary Science','225628',TRUE),
('Sociology','4119684',TRUE),
('Interdisciplinary Studies Field','7734960',TRUE),
('College Writing','5291686',TRUE),
('Freshman and Sophomore Seminars','6712098',TRUE),
('Freshman and Sophomore Seminars','7736123',FALSE),
('Freshman and Sophomore Seminars','5562743',TRUE),
('Freshman and Sophomore Seminars','8112725',FALSE),
('Freshman and Sophomore Seminars','5096541',TRUE),
('Media Studies','8112725',TRUE),
('L&S Arts and Humanities','3213874',TRUE),
('Philosophy','100',TRUE),
('Philosophy','300',TRUE),
('Philosophy','400',TRUE),
('Philosophy','500',TRUE),
('Computational Biology','1689443',TRUE),
('Physical Education','139468',TRUE),
('Gender and Women''s Studies','1042209',TRUE),
('Music','2570154',TRUE);

INSERT INTO department_members (department_id, user_id, can_receive_communications, created_at, updated_at)
SELECT
  d.id, u.id, du.can_receive_communications, now(), now()
FROM
  dept_uids du
JOIN
  departments d ON du.dept_name = d.dept_name
JOIN
  users u on du.uid = u.uid;

DROP TABLE dept_uids;

INSERT INTO user_department_forms (user_id, department_form_id, created_at, updated_at)
SELECT
  u.id, df.id, now(), now()
FROM
  users u, department_forms df
WHERE
  (u.uid = '100' AND df.name = 'PHILOS')
  OR (u.uid = '5013530' AND df.name = 'ANCIENT_HISTORY')
  OR (u.uid = '6982398' AND df.name = 'ANCIENT_HISTORY')
  OR (u.uid = '5013530' AND df.name = 'HISTORY')
  OR (u.uid = '6982398' AND df.name = 'HISTORY')
  OR (u.uid = '1007025' AND df.name = 'MELC');

COMMIT;