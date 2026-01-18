

-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Hôte : 127.0.0.1:3306
-- Généré le : jeu. 01 jan. 2026 à 11:07
-- Version du serveur : 8.2.0
-- Version de PHP : 8.2.13

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de données : `planning_examens`
--

DELIMITER $$
--
-- Procédures
--
DROP PROCEDURE IF EXISTS `GenererPlanningExamen`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `GenererPlanningExamen` (IN `p_date_debut` DATE, IN `p_date_fin` DATE, IN `p_session` VARCHAR(20), IN `p_annee_scolaire` YEAR)   BEGIN
    DECLARE v_module_id INT;
    DECLARE v_formation_id INT;
    DECLARE v_nb_etudiants INT;
    DECLARE v_salle_id INT;
    DECLARE v_professeur_id INT;
    DECLARE v_surveillant_id INT;
    DECLARE v_date_examen DATE;
    DECLARE v_heure_debut TIME;
    DECLARE v_heure_fin TIME;
    DECLARE v_duree INT DEFAULT 120;
    DECLARE v_finished INT DEFAULT 0;
    
    -- Curseur pour les modules à planifier
    DECLARE module_cursor CURSOR FOR 
    SELECT m.id, m.formation_id, m.professeur_id,
           COUNT(i.etudiant_id) as nb_etudiants
    FROM modules m
    LEFT JOIN inscriptions i ON m.id = i.module_id
    WHERE i.annee_scolaire = p_annee_scolaire
    GROUP BY m.id
    ORDER BY m.formation_id, nb_etudiants DESC;
    
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_finished = 1;
    
    -- Variables pour la gestion des dates et heures
    SET v_date_examen = p_date_debut;
    SET v_heure_debut = '08:00:00';
    
    -- Supprimer les anciens examens non confirmés pour cette session
    DELETE FROM examens 
    WHERE session = p_session 
    AND annee_scolaire = p_annee_scolaire
    AND statut = 'planifié';
    
    OPEN module_cursor;
    
    module_loop: LOOP
        FETCH module_cursor INTO v_module_id, v_formation_id, v_professeur_id, v_nb_etudiants;
        
        IF v_finished = 1 THEN
            LEAVE module_loop;
        END IF;
        
        -- Trouver une salle disponible avec capacité suffisante
        SELECT id INTO v_salle_id
        FROM lieu_examen 
        WHERE capacite >= v_nb_etudiants
        AND disponible = TRUE
        AND id NOT IN (
            SELECT salle_id 
            FROM examens 
            WHERE date_examen = v_date_examen 
            AND heure_debut = v_heure_debut
            AND statut != 'annulé'
        )
        ORDER BY capacite ASC, type DESC
        LIMIT 1;
        
        -- Trouver un surveillant (professeur du même département)
        SELECT p.id INTO v_surveillant_id
        FROM professeurs p
        JOIN modules m ON p.dept_id = (
            SELECT dept_id FROM formations WHERE id = v_formation_id
        )
        WHERE p.id != v_professeur_id
        AND p.id NOT IN (
            SELECT surveillant_id 
            FROM examens 
            WHERE date_examen = v_date_examen
            AND statut != 'annulé'
            GROUP BY surveillant_id
            HAVING COUNT(*) >= 3  -- Max 3 surveillances par jour
        )
        LIMIT 1;
        
        -- Insérer l'examen
        INSERT INTO examens (
            module_id, professeur_id, surveillant_id, salle_id,
            date_examen, heure_debut, heure_fin, duree_minutes,
            statut, session, annee_scolaire
        ) VALUES (
            v_module_id, v_professeur_id, v_surveillant_id, v_salle_id,
            v_date_examen, v_heure_debut,
            ADDTIME(v_heure_debut, SEC_TO_TIME(v_duree * 60)),
            v_duree, 'planifié', p_session, p_annee_scolaire
        );
        
        -- Passer à l'horaire suivant
        SET v_heure_debut = ADDTIME(v_heure_debut, '02:30:00');  -- 2h30 entre examens
        
        -- Si fin de journée, passer au jour suivant
        IF v_heure_debut >= '18:00:00' THEN
            SET v_date_examen = DATE_ADD(v_date_examen, INTERVAL 1 DAY);
            SET v_heure_debut = '08:00:00';
            
            -- Vérifier si on dépasse la date de fin
            IF v_date_examen > p_date_fin THEN
                SET v_date_examen = p_date_debut;
            END IF;
        END IF;
        
    END LOOP module_loop;
    
    CLOSE module_cursor;
    
    -- Enregistrer les statistiques
    INSERT INTO stats_generation (total_examens, taux_occupation_salles, utilisateur)
    SELECT 
        COUNT(*) as total_examens,
        ROUND((COUNT(DISTINCT salle_id) / (SELECT COUNT(*) FROM lieu_examen WHERE disponible = TRUE)) * 100, 2),
        'Admin'
    FROM examens 
    WHERE session = p_session 
    AND annee_scolaire = p_annee_scolaire;
    
END$$

--
-- Fonctions
--
DROP FUNCTION IF EXISTS `VerifierConflitsExamen`$$
CREATE DEFINER=`root`@`localhost` FUNCTION `VerifierConflitsExamen` (`p_salle_id` INT, `p_date` DATE, `p_heure_debut` TIME, `p_duree_minutes` INT) RETURNS INT  BEGIN
    DECLARE v_conflict_count INT;
    
    SELECT COUNT(*) INTO v_conflict_count
    FROM examens e
    WHERE e.salle_id = p_salle_id
    AND e.date_examen = p_date
    AND e.statut != 'annulé'
    AND (
        (p_heure_debut BETWEEN e.heure_debut AND e.heure_fin)
        OR (ADDTIME(p_heure_debut, SEC_TO_TIME(p_duree_minutes * 60)) BETWEEN e.heure_debut AND e.heure_fin)
        OR (e.heure_debut BETWEEN p_heure_debut AND ADDTIME(p_heure_debut, SEC_TO_TIME(p_duree_minutes * 60)))
    );
    
    RETURN v_conflict_count;
END$$

DELIMITER ;

-- --------------------------------------------------------

--
-- Structure de la table `contraintes`
--

DROP TABLE IF EXISTS `contraintes`;
CREATE TABLE IF NOT EXISTS `contraintes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `type` enum('Etudiant','Professeur','Salle','Departement') NOT NULL,
  `entite_id` int DEFAULT NULL,
  `jour` date DEFAULT NULL,
  `heure_debut` time DEFAULT NULL,
  `heure_fin` time DEFAULT NULL,
  `raison` text,
  PRIMARY KEY (`id`),
  KEY `idx_type_entite` (`type`,`entite_id`)
) ENGINE=MyISAM AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Déchargement des données de la table `contraintes`
--

INSERT INTO `contraintes` (`id`, `type`, `entite_id`, `jour`, `heure_debut`, `heure_fin`, `raison`) VALUES
(1, 'Professeur', 1, '2024-01-24', '08:00:00', '12:00:00', 'Réunion départementale'),
(2, 'Professeur', 2, '2024-01-19', '14:00:00', '18:00:00', 'Conférence'),
(3, 'Salle', 1, '2024-01-22', '08:00:00', '12:00:00', 'Maintenance'),
(4, 'Salle', 4, '2024-01-25', '14:00:00', '18:00:00', 'Réserve pour jury'),
(5, 'Departement', 1, '2024-01-18', '08:00:00', '10:00:00', 'Assemblée générale');

-- --------------------------------------------------------

--
-- Structure de la table `departements`
--

DROP TABLE IF EXISTS `departements`;
CREATE TABLE IF NOT EXISTS `departements` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nom` varchar(100) NOT NULL,
  `responsable_id` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Déchargement des données de la table `departements`
--

INSERT INTO `departements` (`id`, `nom`, `responsable_id`) VALUES
(1, 'Informatique', 1),
(2, 'Mathématiques', 7),
(3, 'Physique', 10),
(4, 'Chimie', 11),
(5, 'Biologie', 12),
(6, 'Sciences Humaines', NULL),
(7, 'Droit', NULL),
(8, 'Informatique', NULL),
(9, 'Mathématiques', NULL),
(10, 'Physique', NULL),
(11, 'Chimie', NULL),
(12, 'Biologie', NULL),
(13, 'Sciences Humaines', NULL),
(14, 'Droit', NULL),
(15, 'Informatique', NULL),
(16, 'Mathématiques', NULL),
(17, 'Physique', NULL),
(18, 'Chimie', NULL),
(19, 'Biologie', NULL),
(20, 'Sciences Humaines', NULL),
(21, 'Droit', NULL);

-- --------------------------------------------------------

--
-- Structure de la table `etudiants`
--

DROP TABLE IF EXISTS `etudiants`;
CREATE TABLE IF NOT EXISTS `etudiants` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nom` varchar(100) NOT NULL,
  `prenom` varchar(100) NOT NULL,
  `formation_id` int DEFAULT NULL,
  `promo` year DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `formation_id` (`formation_id`)
) ENGINE=MyISAM AUTO_INCREMENT=61 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Déchargement des données de la table `etudiants`
--

INSERT INTO `etudiants` (`id`, `nom`, `prenom`, `formation_id`, `promo`) VALUES
(1, 'Dupont', 'Jean', 1, '2024'),
(2, 'Martin', 'Marie', 1, '2024'),
(3, 'Bernard', 'Pierre', 1, '2024'),
(4, 'Thomas', 'Sophie', 1, '2024'),
(5, 'Robert', 'Luc', 1, '2024'),
(6, 'Richard', 'Claire', 1, '2024'),
(7, 'Petit', 'Nicolas', 1, '2024'),
(8, 'Durand', 'Isabelle', 1, '2024'),
(9, 'Leroy', 'Antoine', 2, '2024'),
(10, 'Moreau', 'Élise', 2, '2024'),
(11, 'Simon', 'David', 2, '2024'),
(12, 'Laurent', 'Sarah', 3, '2024'),
(13, 'Michel', 'Alexandre', 3, '2024'),
(14, 'Lefebvre', 'Thomas', 4, '2024'),
(15, 'Garcia', 'Camille', 4, '2024'),
(16, 'Roux', 'Paul', 6, '2024'),
(17, 'Vincent', 'Julie', 6, '2024'),
(18, 'Fournier', 'Marc', 9, '2024'),
(19, 'Mercier', 'Laura', 11, '2024'),
(20, 'Blanc', 'François', 13, '2024'),
(21, 'Dupont', 'Jean', 1, '2024'),
(22, 'Martin', 'Marie', 1, '2024'),
(23, 'Bernard', 'Pierre', 1, '2024'),
(24, 'Thomas', 'Sophie', 1, '2024'),
(25, 'Robert', 'Luc', 1, '2024'),
(26, 'Richard', 'Claire', 1, '2024'),
(27, 'Petit', 'Nicolas', 1, '2024'),
(28, 'Durand', 'Isabelle', 1, '2024'),
(29, 'Leroy', 'Antoine', 2, '2024'),
(30, 'Moreau', 'Élise', 2, '2024'),
(31, 'Simon', 'David', 2, '2024'),
(32, 'Laurent', 'Sarah', 3, '2024'),
(33, 'Michel', 'Alexandre', 3, '2024'),
(34, 'Lefebvre', 'Thomas', 4, '2024'),
(35, 'Garcia', 'Camille', 4, '2024'),
(36, 'Roux', 'Paul', 6, '2024'),
(37, 'Vincent', 'Julie', 6, '2024'),
(38, 'Fournier', 'Marc', 9, '2024'),
(39, 'Mercier', 'Laura', 11, '2024'),
(40, 'Blanc', 'François', 13, '2024'),
(41, 'Dupont', 'Jean', 1, '2024'),
(42, 'Martin', 'Marie', 1, '2024'),
(43, 'Bernard', 'Pierre', 1, '2024'),
(44, 'Thomas', 'Sophie', 1, '2024'),
(45, 'Robert', 'Luc', 1, '2024'),
(46, 'Richard', 'Claire', 1, '2024'),
(47, 'Petit', 'Nicolas', 1, '2024'),
(48, 'Durand', 'Isabelle', 1, '2024'),
(49, 'Leroy', 'Antoine', 2, '2024'),
(50, 'Moreau', 'Élise', 2, '2024'),
(51, 'Simon', 'David', 2, '2024'),
(52, 'Laurent', 'Sarah', 3, '2024'),
(53, 'Michel', 'Alexandre', 3, '2024'),
(54, 'Lefebvre', 'Thomas', 4, '2024'),
(55, 'Garcia', 'Camille', 4, '2024'),
(56, 'Roux', 'Paul', 6, '2024'),
(57, 'Vincent', 'Julie', 6, '2024'),
(58, 'Fournier', 'Marc', 9, '2024'),
(59, 'Mercier', 'Laura', 11, '2024'),
(60, 'Blanc', 'François', 13, '2024');

-- --------------------------------------------------------

--
-- Structure de la table `examens`
--

DROP TABLE IF EXISTS `examens`;
CREATE TABLE IF NOT EXISTS `examens` (
  `id` int NOT NULL AUTO_INCREMENT,
  `module_id` int NOT NULL,
  `professeur_id` int DEFAULT NULL,
  `surveillant_id` int DEFAULT NULL,
  `salle_id` int NOT NULL,
  `date_examen` date NOT NULL,
  `heure_debut` time NOT NULL,
  `heure_fin` time NOT NULL,
  `duree_minutes` int DEFAULT '120',
  `statut` enum('planifié','confirmé','annulé') DEFAULT 'planifié',
  `session` enum('Principale','Rattrapage') DEFAULT 'Principale',
  `annee_scolaire` year DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `module_id` (`module_id`),
  KEY `professeur_id` (`professeur_id`),
  KEY `surveillant_id` (`surveillant_id`),
  KEY `idx_date` (`date_examen`),
  KEY `idx_salle_date` (`salle_id`,`date_examen`,`heure_debut`),
  KEY `idx_examens_date_session` (`date_examen`,`session`,`annee_scolaire`)
) ENGINE=MyISAM AUTO_INCREMENT=40 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Déchargement des données de la table `examens`
--

INSERT INTO `examens` (`id`, `module_id`, `professeur_id`, `surveillant_id`, `salle_id`, `date_examen`, `heure_debut`, `heure_fin`, `duree_minutes`, `statut`, `session`, `annee_scolaire`) VALUES
(1, 1, 2, 3, 1, '2025-12-22', '08:00:00', '10:00:00', 120, 'confirmé', 'Principale', '2025'),
(2, 2, 1, 2, 2, '2024-12-25', '08:00:00', '10:00:00', 120, 'confirmé', 'Principale', '2025'),
(3, 26, 7, 8, 3, '2024-01-15', '08:00:00', '10:00:00', 120, 'confirmé', 'Principale', '2024'),
(4, 3, 3, 2, 4, '2025-12-23', '09:00:00', '11:00:00', 120, 'confirmé', 'Principale', '2025'),
(5, 5, 4, 6, 5, '2025-12-24', '09:00:00', '11:00:00', 120, 'confirmé', 'Principale', '2025'),
(6, 29, 10, 11, 6, '2024-01-16', '09:00:00', '11:00:00', 120, 'confirmé', 'Principale', '2024'),
(7, 4, 3, 5, 7, '2024-01-17', '10:00:00', '12:00:00', 120, 'planifié', 'Principale', '2024'),
(8, 6, 3, 4, 7, '2024-01-17', '10:30:00', '12:30:00', 120, 'planifié', 'Principale', '2024'),
(9, 7, 6, 1, 8, '2024-01-17', '10:00:00', '12:00:00', 120, 'planifié', 'Principale', '2024'),
(10, 31, 11, 12, 9, '2024-01-17', '10:00:00', '12:00:00', 120, 'planifié', 'Principale', '2024'),
(11, 9, 1, 2, 1, '2024-01-18', '14:00:00', '16:00:00', 120, 'planifié', 'Principale', '2024'),
(12, 16, 6, 9, 2, '2024-01-18', '14:00:00', '16:00:00', 120, 'confirmé', 'Principale', '2024'),
(13, 21, 5, 3, 12, '2024-01-18', '14:00:00', '16:00:00', 120, 'planifié', 'Principale', '2024'),
(14, 32, 12, 11, 10, '2024-01-18', '14:00:00', '16:00:00', 120, 'planifié', 'Principale', '2024'),
(15, 10, 2, 1, 4, '2024-01-19', '08:00:00', '10:00:00', 120, 'planifié', 'Principale', '2024'),
(16, 17, 2, 6, 5, '2024-01-19', '08:00:00', '10:00:00', 120, 'annulé', 'Principale', '2024'),
(17, 22, 3, 5, 13, '2024-01-19', '08:00:00', '10:00:00', 120, 'planifié', 'Principale', '2024'),
(18, 27, 8, 7, 6, '2024-01-19', '08:00:00', '10:00:00', 120, 'planifié', 'Principale', '2024'),
(19, 11, 5, 3, 7, '2024-01-20', '09:00:00', '11:00:00', 120, 'planifié', 'Principale', '2024'),
(20, 30, 10, 11, 8, '2024-01-20', '09:00:00', '11:00:00', 120, 'planifié', 'Principale', '2024'),
(21, 1, 1, 2, 1, '2024-01-22', '08:00:00', '10:00:00', 120, 'planifié', 'Principale', '2024'),
(22, 1, 1, 3, 2, '2024-01-23', '08:00:00', '10:00:00', 120, 'planifié', 'Principale', '2024'),
(23, 9, 1, 4, 3, '2024-01-23', '08:00:00', '10:00:00', 120, 'planifié', 'Principale', '2024'),
(24, 4, 3, 5, 4, '2024-01-24', '14:00:00', '16:00:00', 120, 'planifié', 'Principale', '2024'),
(25, 5, 4, 1, 5, '2024-01-25', '09:00:00', '11:00:00', 120, 'planifié', 'Principale', '2024'),
(26, 6, 3, 2, 6, '2024-01-25', '09:00:00', '11:00:00', 120, 'planifié', 'Principale', '2024'),
(27, 7, 6, 3, 7, '2024-01-25', '09:00:00', '11:00:00', 120, 'planifié', 'Principale', '2024'),
(28, 2, 2, 1, 8, '2024-01-26', '10:00:00', '12:00:00', 120, 'planifié', 'Principale', '2024'),
(29, 3, 3, 4, 9, '2024-01-26', '10:00:00', '12:00:00', 120, 'planifié', 'Principale', '2024'),
(30, 16, 6, 9, 1, '2024-01-27', '14:00:00', '16:00:00', 120, 'planifié', 'Principale', '2024'),
(31, 17, 2, 6, 2, '2024-01-27', '14:00:00', '16:00:00', 120, 'planifié', 'Principale', '2024'),
(32, 21, 5, 3, 12, '2024-01-29', '08:00:00', '10:00:00', 120, 'planifié', 'Principale', '2024'),
(33, 22, 3, 5, 13, '2024-01-29', '08:00:00', '10:00:00', 120, 'planifié', 'Principale', '2024'),
(34, 26, 7, 8, 3, '2024-01-30', '09:00:00', '11:00:00', 120, 'planifié', 'Principale', '2024'),
(35, 27, 8, 7, 4, '2024-01-31', '14:00:00', '16:00:00', 120, 'planifié', 'Principale', '2024'),
(36, 29, 10, 11, 5, '2024-02-01', '10:00:00', '12:00:00', 120, 'planifié', 'Principale', '2024'),
(37, 30, 10, 12, 6, '2024-02-01', '10:00:00', '12:00:00', 120, 'planifié', 'Principale', '2024'),
(38, 31, 11, 10, 7, '2024-02-02', '08:00:00', '10:00:00', 120, 'planifié', 'Principale', '2024'),
(39, 32, 12, 11, 8, '2024-02-02', '08:00:00', '10:00:00', 120, 'planifié', 'Principale', '2024');

-- --------------------------------------------------------

--
-- Structure de la table `formations`
--

DROP TABLE IF EXISTS `formations`;
CREATE TABLE IF NOT EXISTS `formations` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nom` varchar(150) NOT NULL,
  `dept_id` int DEFAULT NULL,
  `nb_modules` int DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `dept_id` (`dept_id`)
) ENGINE=MyISAM AUTO_INCREMENT=40 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Déchargement des données de la table `formations`
--

INSERT INTO `formations` (`id`, `nom`, `dept_id`, `nb_modules`) VALUES
(1, 'Licence Informatique', 1, 8),
(2, 'Master Informatique', 1, 10),
(3, 'Master Data Science', 1, 10),
(4, 'Master Cybersécurité', 1, 10),
(5, 'Licence MIAGE', 1, 8),
(6, 'Licence Mathématiques', 2, 8),
(7, 'Master Mathématiques Appliquées', 2, 10),
(8, 'Master Statistiques', 2, 10),
(9, 'Licence Physique', 3, 8),
(10, 'Master Physique Quantique', 3, 10),
(11, 'Licence Chimie', 4, 8),
(12, 'Licence Biologie', 5, 8),
(13, 'Master Biotechnologies', 5, 10),
(14, 'Licence Informatique', 1, 8),
(15, 'Master Informatique', 1, 10),
(16, 'Master Data Science', 1, 10),
(17, 'Master Cybersécurité', 1, 10),
(18, 'Licence MIAGE', 1, 8),
(19, 'Licence Mathématiques', 2, 8),
(20, 'Master Mathématiques Appliquées', 2, 10),
(21, 'Master Statistiques', 2, 10),
(22, 'Licence Physique', 3, 8),
(23, 'Master Physique Quantique', 3, 10),
(24, 'Licence Chimie', 4, 8),
(25, 'Licence Biologie', 5, 8),
(26, 'Master Biotechnologies', 5, 10),
(27, 'Licence Informatique', 1, 8),
(28, 'Master Informatique', 1, 10),
(29, 'Master Data Science', 1, 10),
(30, 'Master Cybersécurité', 1, 10),
(31, 'Licence MIAGE', 1, 8),
(32, 'Licence Mathématiques', 2, 8),
(33, 'Master Mathématiques Appliquées', 2, 10),
(34, 'Master Statistiques', 2, 10),
(35, 'Licence Physique', 3, 8),
(36, 'Master Physique Quantique', 3, 10),
(37, 'Licence Chimie', 4, 8),
(38, 'Licence Biologie', 5, 8),
(39, 'Master Biotechnologies', 5, 10);

-- --------------------------------------------------------

--
-- Structure de la table `inscriptions`
--

DROP TABLE IF EXISTS `inscriptions`;
CREATE TABLE IF NOT EXISTS `inscriptions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `etudiant_id` int NOT NULL,
  `module_id` int NOT NULL,
  `annee_scolaire` year DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_inscription` (`etudiant_id`,`module_id`,`annee_scolaire`),
  KEY `module_id` (`module_id`),
  KEY `idx_inscriptions_annee` (`annee_scolaire`,`module_id`)
) ENGINE=MyISAM AUTO_INCREMENT=49 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Déchargement des données de la table `inscriptions`
--

INSERT INTO `inscriptions` (`id`, `etudiant_id`, `module_id`, `annee_scolaire`) VALUES
(1, 1, 1, '2024'),
(2, 1, 2, '2024'),
(3, 1, 3, '2024'),
(4, 1, 4, '2024'),
(5, 1, 5, '2024'),
(6, 1, 6, '2024'),
(7, 2, 1, '2024'),
(8, 2, 2, '2024'),
(9, 2, 3, '2024'),
(10, 2, 4, '2024'),
(11, 2, 5, '2024'),
(12, 2, 6, '2024'),
(13, 3, 1, '2024'),
(14, 3, 2, '2024'),
(15, 3, 3, '2024'),
(16, 3, 4, '2024'),
(17, 3, 5, '2024'),
(18, 3, 6, '2024'),
(19, 4, 1, '2024'),
(20, 4, 2, '2024'),
(21, 4, 3, '2024'),
(22, 4, 4, '2024'),
(23, 4, 5, '2024'),
(24, 4, 6, '2024'),
(25, 5, 1, '2024'),
(26, 5, 2, '2024'),
(27, 5, 3, '2024'),
(28, 5, 4, '2024'),
(29, 5, 5, '2024'),
(30, 5, 6, '2024'),
(31, 9, 9, '2024'),
(32, 9, 10, '2024'),
(33, 9, 11, '2024'),
(34, 10, 9, '2024'),
(35, 10, 10, '2024'),
(36, 10, 11, '2024'),
(37, 13, 16, '2024'),
(38, 13, 17, '2024'),
(39, 14, 16, '2024'),
(40, 14, 17, '2024'),
(41, 15, 21, '2024'),
(42, 15, 22, '2024'),
(43, 17, 26, '2024'),
(44, 17, 27, '2024'),
(45, 20, 29, '2024'),
(46, 20, 30, '2024'),
(47, 21, 31, '2024'),
(48, 22, 32, '2024');

-- --------------------------------------------------------

--
-- Structure de la table `lieu_examen`
--

DROP TABLE IF EXISTS `lieu_examen`;
CREATE TABLE IF NOT EXISTS `lieu_examen` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nom` varchar(100) NOT NULL,
  `capacite` int NOT NULL,
  `type` enum('Amphi','Salle','Labo') DEFAULT 'Salle',
  `batiment` varchar(50) DEFAULT NULL,
  `equipement` text,
  `disponible` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`id`),
  KEY `idx_lieu_capacite` (`capacite`,`type`,`disponible`)
) ENGINE=MyISAM AUTO_INCREMENT=40 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Déchargement des données de la table `lieu_examen`
--

INSERT INTO `lieu_examen` (`id`, `nom`, `capacite`, `type`, `batiment`, `equipement`, `disponible`) VALUES
(1, 'Amphi A', 300, 'Amphi', 'Bâtiment Principal', 'Projecteur, Micro, Tableau numérique', 1),
(2, 'Amphi B', 250, 'Amphi', 'Bâtiment Principal', 'Projecteur, Micro', 1),
(3, 'Amphi C', 200, 'Amphi', 'Bâtiment Principal', 'Projecteur', 1),
(4, 'Salle 101', 30, 'Salle', 'Bâtiment A', 'Tableau blanc', 1),
(5, 'Salle 102', 30, 'Salle', 'Bâtiment A', 'Tableau blanc', 1),
(6, 'Salle 103', 30, 'Salle', 'Bâtiment A', 'Tableau blanc', 1),
(7, 'Salle 201', 40, 'Salle', 'Bâtiment B', 'Tableau numérique', 1),
(8, 'Salle 202', 40, 'Salle', 'Bâtiment B', 'Tableau numérique', 1),
(9, 'Salle 301', 25, 'Salle', 'Bâtiment C', 'Tableau blanc', 1),
(10, 'Salle 302', 25, 'Salle', 'Bâtiment C', 'Tableau blanc', 1),
(11, 'Labo Info 1', 25, 'Labo', 'Bâtiment Informatique', '25 PC, Projecteur', 1),
(12, 'Labo Info 2', 25, 'Labo', 'Bâtiment Informatique', '25 PC, Projecteur', 1),
(13, 'Labo Info 3', 20, 'Labo', 'Bâtiment Informatique', '20 PC, Tableau numérique', 1),
(14, 'Amphi A', 300, 'Amphi', 'Bâtiment Principal', 'Projecteur, Micro, Tableau numérique', 1),
(15, 'Amphi B', 250, 'Amphi', 'Bâtiment Principal', 'Projecteur, Micro', 1),
(16, 'Amphi C', 200, 'Amphi', 'Bâtiment Principal', 'Projecteur', 1),
(17, 'Salle 101', 30, 'Salle', 'Bâtiment A', 'Tableau blanc', 1),
(18, 'Salle 102', 30, 'Salle', 'Bâtiment A', 'Tableau blanc', 1),
(19, 'Salle 103', 30, 'Salle', 'Bâtiment A', 'Tableau blanc', 1),
(20, 'Salle 201', 40, 'Salle', 'Bâtiment B', 'Tableau numérique', 1),
(21, 'Salle 202', 40, 'Salle', 'Bâtiment B', 'Tableau numérique', 1),
(22, 'Salle 301', 25, 'Salle', 'Bâtiment C', 'Tableau blanc', 1),
(23, 'Salle 302', 25, 'Salle', 'Bâtiment C', 'Tableau blanc', 1),
(24, 'Labo Info 1', 25, 'Labo', 'Bâtiment Informatique', '25 PC, Projecteur', 1),
(25, 'Labo Info 2', 25, 'Labo', 'Bâtiment Informatique', '25 PC, Projecteur', 1),
(26, 'Labo Info 3', 20, 'Labo', 'Bâtiment Informatique', '20 PC, Tableau numérique', 1),
(27, 'Amphi A', 300, 'Amphi', 'Bâtiment Principal', 'Projecteur, Micro, Tableau numérique', 1),
(28, 'Amphi B', 250, 'Amphi', 'Bâtiment Principal', 'Projecteur, Micro', 1),
(29, 'Amphi C', 200, 'Amphi', 'Bâtiment Principal', 'Projecteur', 1),
(30, 'Salle 101', 30, 'Salle', 'Bâtiment A', 'Tableau blanc', 1),
(31, 'Salle 102', 30, 'Salle', 'Bâtiment A', 'Tableau blanc', 1),
(32, 'Salle 103', 30, 'Salle', 'Bâtiment A', 'Tableau blanc', 1),
(33, 'Salle 201', 40, 'Salle', 'Bâtiment B', 'Tableau numérique', 1),
(34, 'Salle 202', 40, 'Salle', 'Bâtiment B', 'Tableau numérique', 1),
(35, 'Salle 301', 25, 'Salle', 'Bâtiment C', 'Tableau blanc', 1),
(36, 'Salle 302', 25, 'Salle', 'Bâtiment C', 'Tableau blanc', 1),
(37, 'Labo Info 1', 25, 'Labo', 'Bâtiment Informatique', '25 PC, Projecteur', 1),
(38, 'Labo Info 2', 25, 'Labo', 'Bâtiment Informatique', '25 PC, Projecteur', 1),
(39, 'Labo Info 3', 20, 'Labo', 'Bâtiment Informatique', '20 PC, Tableau numérique', 1);

-- --------------------------------------------------------

--
-- Structure de la table `modules`
--

DROP TABLE IF EXISTS `modules`;
CREATE TABLE IF NOT EXISTS `modules` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nom` varchar(200) NOT NULL,
  `credits` int DEFAULT '3',
  `formation_id` int DEFAULT NULL,
  `professeur_id` int DEFAULT NULL,
  `heures_cours` int DEFAULT '30',
  PRIMARY KEY (`id`),
  KEY `idx_modules_formation` (`formation_id`,`professeur_id`)
) ENGINE=MyISAM AUTO_INCREMENT=88 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Déchargement des données de la table `modules`
--

INSERT INTO `modules` (`id`, `nom`, `credits`, `formation_id`, `professeur_id`, `heures_cours`) VALUES
(1, 'Algorithmique et Programmation', 6, 1, 1, 60),
(2, 'Base de Données', 6, 1, 2, 60),
(3, 'Architecture des Ordinateurs', 6, 1, 3, 60),
(4, 'Systèmes d\'Exploitation', 6, 1, 3, 60),
(5, 'Programmation Web', 6, 2, 4, 60),
(6, 'Réseaux Informatiques', 6, 1, 3, 60),
(7, 'Introduction à l\'IA', 6, 1, 6, 60),
(8, 'Projet Informatique', 6, 1, 1, 60),
(9, 'Algorithmique Avancée', 6, 2, 1, 60),
(10, 'Bases de Données Avancées', 6, 2, 2, 60),
(11, 'Sécurité Informatique', 6, 2, 5, 60),
(12, 'Cloud Computing', 6, 2, 3, 60),
(13, 'Développement Mobile', 6, 2, 4, 60),
(14, 'Machine Learning', 6, 3, 6, 60),
(15, 'Big Data', 6, 3, 2, 60),
(16, 'Data Mining', 6, 3, 6, 60),
(17, 'Statistiques pour Data Science', 6, 3, 9, 60),
(18, 'Visualisation de Données', 6, 3, 4, 60),
(19, 'Cryptographie', 6, 4, 5, 60),
(20, 'Sécurité Réseaux', 6, 4, 3, 60),
(21, 'Forensique Numérique', 6, 4, 5, 60),
(22, 'Sécurité Web', 6, 4, 4, 60),
(23, 'Algèbre Linéaire', 6, 6, 7, 60),
(24, 'Analyse Réelle', 6, 6, 8, 60),
(25, 'Probabilités', 6, 6, 9, 60),
(26, 'Mécanique Classique', 6, 9, 10, 60),
(27, 'Électromagnétisme', 6, 9, 10, 60),
(28, 'Chimie Générale', 6, 11, 11, 60),
(29, 'Biologie Cellulaire', 6, 13, 12, 60),
(30, 'Algorithmique et Programmation', 6, 1, 1, 60),
(31, 'Base de Données', 6, 1, 2, 60),
(32, 'Architecture des Ordinateurs', 6, 1, 3, 60),
(33, 'Systèmes d\'Exploitation', 6, 1, 3, 60),
(34, 'Programmation Web', 6, 1, 4, 60),
(35, 'Réseaux Informatiques', 6, 1, 3, 60),
(36, 'Introduction à l\'IA', 6, 1, 6, 60),
(37, 'Projet Informatique', 6, 1, 1, 60),
(38, 'Algorithmique Avancée', 6, 2, 1, 60),
(39, 'Bases de Données Avancées', 6, 2, 2, 60),
(40, 'Sécurité Informatique', 6, 2, 5, 60),
(41, 'Cloud Computing', 6, 2, 3, 60),
(42, 'Développement Mobile', 6, 2, 4, 60),
(43, 'Machine Learning', 6, 3, 6, 60),
(44, 'Big Data', 6, 3, 2, 60),
(45, 'Data Mining', 6, 3, 6, 60),
(46, 'Statistiques pour Data Science', 6, 3, 9, 60),
(47, 'Visualisation de Données', 6, 3, 4, 60),
(48, 'Cryptographie', 6, 4, 5, 60),
(49, 'Sécurité Réseaux', 6, 4, 3, 60),
(50, 'Forensique Numérique', 6, 4, 5, 60),
(51, 'Sécurité Web', 6, 4, 4, 60),
(52, 'Algèbre Linéaire', 6, 6, 7, 60),
(53, 'Analyse Réelle', 6, 6, 8, 60),
(54, 'Probabilités', 6, 6, 9, 60),
(55, 'Mécanique Classique', 6, 9, 10, 60),
(56, 'Électromagnétisme', 6, 9, 10, 60),
(57, 'Chimie Générale', 6, 11, 11, 60),
(58, 'Biologie Cellulaire', 6, 13, 12, 60),
(59, 'Algorithmique et Programmation', 6, 1, 1, 60),
(60, 'Base de Données', 6, 1, 2, 60),
(61, 'Architecture des Ordinateurs', 6, 1, 3, 60),
(62, 'Systèmes d\'Exploitation', 6, 1, 3, 60),
(63, 'Programmation Web', 6, 1, 4, 60),
(64, 'Réseaux Informatiques', 6, 1, 3, 60),
(65, 'Introduction à l\'IA', 6, 1, 6, 60),
(66, 'Projet Informatique', 6, 1, 1, 60),
(67, 'Algorithmique Avancée', 6, 2, 1, 60),
(68, 'Bases de Données Avancées', 6, 2, 2, 60),
(69, 'Sécurité Informatique', 6, 2, 5, 60),
(70, 'Cloud Computing', 6, 2, 3, 60),
(71, 'Développement Mobile', 6, 2, 4, 60),
(72, 'Machine Learning', 6, 3, 6, 60),
(73, 'Big Data', 6, 3, 2, 60),
(74, 'Data Mining', 6, 3, 6, 60),
(75, 'Statistiques pour Data Science', 6, 3, 9, 60),
(76, 'Visualisation de Données', 6, 3, 4, 60),
(77, 'Cryptographie', 6, 4, 5, 60),
(78, 'Sécurité Réseaux', 6, 4, 3, 60),
(79, 'Forensique Numérique', 6, 4, 5, 60),
(80, 'Sécurité Web', 6, 4, 4, 60),
(81, 'Algèbre Linéaire', 6, 6, 7, 60),
(82, 'Analyse Réelle', 6, 6, 8, 60),
(83, 'Probabilités', 6, 6, 9, 60),
(84, 'Mécanique Classique', 6, 9, 10, 60),
(85, 'Électromagnétisme', 6, 9, 10, 60),
(86, 'Chimie Générale', 6, 11, 11, 60),
(87, 'Biologie Cellulaire', 6, 13, 12, 60);

-- --------------------------------------------------------

--
-- Structure de la table `professeurs`
--

DROP TABLE IF EXISTS `professeurs`;
CREATE TABLE IF NOT EXISTS `professeurs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nom` varchar(100) NOT NULL,
  `prenom` varchar(100) NOT NULL,
  `dept_id` int DEFAULT NULL,
  `specialite` varchar(200) DEFAULT NULL,
  `heures_service` int DEFAULT '192',
  PRIMARY KEY (`id`),
  KEY `idx_professeurs_dept` (`dept_id`)
) ENGINE=MyISAM AUTO_INCREMENT=40 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Déchargement des données de la table `professeurs`
--

INSERT INTO `professeurs` (`id`, `nom`, `prenom`, `dept_id`, `specialite`, `heures_service`) VALUES
(1, 'Martin', 'Jean', 1, 'Algorithmique', 192),
(2, 'Dubois', 'Marie', 1, 'Base de données', 192),
(3, 'Bernard', 'Pierre', 1, 'Réseaux', 192),
(4, 'Thomas', 'Sophie', 1, 'Programmation Web', 192),
(5, 'Robert', 'Luc', 1, 'Sécurité', 192),
(6, 'Richard', 'Claire', 1, 'IA', 192),
(7, 'Durand', 'Paul', 2, 'Algèbre', 192),
(8, 'Simon', 'Julie', 2, 'Analyse', 192),
(9, 'Laurent', 'Marc', 2, 'Statistiques', 192),
(10, 'Michel', 'Anne', 3, 'Mécanique', 192),
(11, 'Lefebvre', 'Philippe', 3, 'Quantique', 192),
(12, 'Garcia', 'Isabelle', 4, 'Chimie organique', 192),
(13, 'Roux', 'François', 5, 'Biologie moléculaire', 192),
(14, 'Martin', 'Jean', 1, 'Algorithmique', 192),
(15, 'Dubois', 'Marie', 1, 'Base de données', 192),
(16, 'Bernard', 'Pierre', 1, 'Réseaux', 192),
(17, 'Thomas', 'Sophie', 1, 'Programmation Web', 192),
(18, 'Robert', 'Luc', 1, 'Sécurité', 192),
(19, 'Richard', 'Claire', 1, 'IA', 192),
(20, 'Durand', 'Paul', 2, 'Algèbre', 192),
(21, 'Simon', 'Julie', 2, 'Analyse', 192),
(22, 'Laurent', 'Marc', 2, 'Statistiques', 192),
(23, 'Michel', 'Anne', 3, 'Mécanique', 192),
(24, 'Lefebvre', 'Philippe', 3, 'Quantique', 192),
(25, 'Garcia', 'Isabelle', 4, 'Chimie organique', 192),
(26, 'Roux', 'François', 5, 'Biologie moléculaire', 192),
(27, 'Martin', 'Jean', 1, 'Algorithmique', 192),
(28, 'Dubois', 'Marie', 1, 'Base de données', 192),
(29, 'Bernard', 'Pierre', 1, 'Réseaux', 192),
(30, 'Thomas', 'Sophie', 1, 'Programmation Web', 192),
(31, 'Robert', 'Luc', 1, 'Sécurité', 192),
(32, 'Richard', 'Claire', 1, 'IA', 192),
(33, 'Durand', 'Paul', 2, 'Algèbre', 192),
(34, 'Simon', 'Julie', 2, 'Analyse', 192),
(35, 'Laurent', 'Marc', 2, 'Statistiques', 192),
(36, 'Michel', 'Anne', 3, 'Mécanique', 192),
(37, 'Lefebvre', 'Philippe', 3, 'Quantique', 192),
(38, 'Garcia', 'Isabelle', 4, 'Chimie organique', 192),
(39, 'Roux', 'François', 5, 'Biologie moléculaire', 192);

-- --------------------------------------------------------

--
-- Structure de la table `stats_generation`
--

DROP TABLE IF EXISTS `stats_generation`;
CREATE TABLE IF NOT EXISTS `stats_generation` (
  `id` int NOT NULL AUTO_INCREMENT,
  `date_generation` datetime DEFAULT CURRENT_TIMESTAMP,
  `duree_generation_secondes` float DEFAULT NULL,
  `total_examens` int DEFAULT NULL,
  `conflits_resolus` int DEFAULT NULL,
  `taux_occupation_salles` float DEFAULT NULL,
  `utilisateur` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Déchargement des données de la table `stats_generation`
--

INSERT INTO `stats_generation` (`id`, `date_generation`, `duree_generation_secondes`, `total_examens`, `conflits_resolus`, `taux_occupation_salles`, `utilisateur`) VALUES
(1, '2025-12-22 12:51:52', NULL, 0, NULL, 0, 'Admin'),
(2, '2025-12-22 12:51:52', 0.0631826, 0, NULL, NULL, 'Admin'),
(3, '2025-12-22 12:55:09', NULL, 0, NULL, 0, 'Admin'),
(4, '2025-12-22 12:55:09', 0.00399375, 0, NULL, NULL, 'Admin'),
(5, '2025-12-22 13:02:08', NULL, 0, NULL, 0, 'Admin'),
(6, '2025-12-22 13:02:08', 0.00795937, 0, NULL, NULL, 'Admin'),
(7, '2025-12-22 13:15:59', NULL, 0, NULL, 0, 'Admin'),
(8, '2025-12-22 13:18:18', NULL, 1, NULL, 11.11, 'Admin'),
(9, '2025-12-22 13:22:13', NULL, 0, NULL, 0, 'Admin'),
(10, '2025-12-22 13:22:13', 0.00594902, 0, NULL, NULL, 'Admin'),
(11, '2025-12-22 13:52:34', 0.0329654, 9, 0, NULL, 'Admin'),
(12, '2025-12-22 14:48:57', 0.0343139, 9, 0, NULL, 'Admin'),
(13, '2025-12-22 16:29:54', 0.0542471, 9, 0, NULL, 'Admin'),
(14, '2025-12-22 16:30:43', 0.0344372, 9, 0, NULL, 'Admin'),
(15, '2025-12-22 16:32:01', 0.0715244, 9, 0, NULL, 'Admin'),
(16, '2024-01-10 10:30:00', 45.2, 25, 3, 65.5, 'admin'),
(17, '2024-01-12 14:15:00', 52.1, 28, 5, 70.2, 'admin'),
(18, '2024-01-14 09:45:00', 38.7, 30, 2, 68.9, 'admin');

-- --------------------------------------------------------

--
-- Structure de la table `utilisateurs`
--

DROP TABLE IF EXISTS `utilisateurs`;
CREATE TABLE IF NOT EXISTS `utilisateurs` (
  `id` int NOT NULL,
  `mot_de_passe` varchar(100) NOT NULL,
  `role` enum('admin','doyen','chef_departement','professeur') NOT NULL,
  `date_creation` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Déchargement des données de la table `utilisateurs`
--

INSERT INTO `utilisateurs` (`id`, `mot_de_passe`, `role`, `date_creation`) VALUES
(45, 'martin123', 'professeur', '2025-12-23 11:49:39'),
(2, 'dubois123', 'professeur', '2025-12-23 11:49:39'),
(3, 'bernard123', 'professeur', '2025-12-23 11:49:39'),
(4, 'thomas123', 'professeur', '2025-12-23 11:49:39'),
(100, 'admin123', 'admin', '2025-12-23 11:49:39'),
(101, 'doyen123', 'doyen', '2025-12-23 11:49:39'),
(1, 'chef123', 'chef_departement', '2025-12-23 11:49:39');

-- --------------------------------------------------------

--
-- Doublure de structure pour la vue `vue_conflits_etudiants`
-- (Voir ci-dessous la vue réelle)
--
DROP VIEW IF EXISTS `vue_conflits_etudiants`;
CREATE TABLE IF NOT EXISTS `vue_conflits_etudiants` (
`etudiant_id` int
,`nom` varchar(100)
,`prenom` varchar(100)
,`jours_examens` bigint
,`dates_examens` text
);

-- --------------------------------------------------------

--
-- Doublure de structure pour la vue `vue_occupation_salles`
-- (Voir ci-dessous la vue réelle)
--
DROP VIEW IF EXISTS `vue_occupation_salles`;
CREATE TABLE IF NOT EXISTS `vue_occupation_salles` (
`salle` varchar(100)
,`type` enum('Amphi','Salle','Labo')
,`capacite` int
,`examens_planifies` bigint
,`taux_occupation_journalier` decimal(29,2)
);

-- --------------------------------------------------------

--
-- Doublure de structure pour la vue `vue_statistiques_departements`
-- (Voir ci-dessous la vue réelle)
--
DROP VIEW IF EXISTS `vue_statistiques_departements`;
CREATE TABLE IF NOT EXISTS `vue_statistiques_departements` (
`departement` varchar(100)
,`nb_formations` bigint
,`nb_modules` bigint
,`nb_examens_planifies` bigint
,`nb_professeurs` bigint
,`capacite_moyenne_salles` decimal(11,0)
);

-- --------------------------------------------------------

--
-- Structure de la vue `vue_conflits_etudiants`
--
DROP TABLE IF EXISTS `vue_conflits_etudiants`;

DROP VIEW IF EXISTS `vue_conflits_etudiants`;
CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `vue_conflits_etudiants`  AS SELECT `e`.`etudiant_id` AS `etudiant_id`, `et`.`nom` AS `nom`, `et`.`prenom` AS `prenom`, count(distinct `ex`.`date_examen`) AS `jours_examens`, group_concat(distinct `ex`.`date_examen` order by `ex`.`date_examen` ASC separator ',') AS `dates_examens` FROM ((`inscriptions` `e` join `examens` `ex` on((`e`.`module_id` = `ex`.`module_id`))) join `etudiants` `et` on((`e`.`etudiant_id` = `et`.`id`))) WHERE (`ex`.`statut` = 'planifié') GROUP BY `e`.`etudiant_id` HAVING (count(distinct `ex`.`date_examen`) < count(distinct `ex`.`id`)) ;

-- --------------------------------------------------------

--
-- Structure de la vue `vue_occupation_salles`
--
DROP TABLE IF EXISTS `vue_occupation_salles`;

DROP VIEW IF EXISTS `vue_occupation_salles`;
CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `vue_occupation_salles`  AS SELECT `le`.`nom` AS `salle`, `le`.`type` AS `type`, `le`.`capacite` AS `capacite`, count(`e`.`id`) AS `examens_planifies`, round((((count(`e`.`id`) * 120) / 480) * 100),2) AS `taux_occupation_journalier` FROM (`lieu_examen` `le` left join `examens` `e` on(((`le`.`id` = `e`.`salle_id`) and (`e`.`statut` = 'planifié')))) GROUP BY `le`.`id` ;

-- --------------------------------------------------------

--
-- Structure de la vue `vue_statistiques_departements`
--
DROP TABLE IF EXISTS `vue_statistiques_departements`;

DROP VIEW IF EXISTS `vue_statistiques_departements`;
CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `vue_statistiques_departements`  AS SELECT `d`.`nom` AS `departement`, count(distinct `f`.`id`) AS `nb_formations`, count(distinct `m`.`id`) AS `nb_modules`, count(distinct `e`.`id`) AS `nb_examens_planifies`, count(distinct `p`.`id`) AS `nb_professeurs`, round(avg(`le`.`capacite`),0) AS `capacite_moyenne_salles` FROM (((((`departements` `d` left join `formations` `f` on((`d`.`id` = `f`.`dept_id`))) left join `modules` `m` on((`f`.`id` = `m`.`formation_id`))) left join `examens` `e` on(((`m`.`id` = `e`.`module_id`) and (`e`.`statut` = 'planifié')))) left join `professeurs` `p` on((`d`.`id` = `p`.`dept_id`))) left join `lieu_examen` `le` on((`le`.`batiment` like concat('%',`d`.`nom`,'%')))) GROUP BY `d`.`id` ;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
