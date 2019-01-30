-- phpMyAdmin SQL Dump
-- version 4.7.4
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Dec 07, 2017 at 07:59 PM
-- Server version: 10.1.28-MariaDB
-- PHP Version: 5.6.32

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `wearables`
--

DELIMITER $$
--
-- Procedures
--
CREATE DEFINER=`root`@`localhost` PROCEDURE `getOrders` ()  BEGIN
	SELECT * FROM `orders`;
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `getOrdersByUser` (IN `id` INT)  BEGIN
	SELECT * FROM orders WHERE user_id = id;
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `getOrderTotal` ()  BEGIN	
	SELECT COUNT(*) as total_orders FROM  `orders`;
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `getProductsByType` (IN `product_type` VARCHAR(50))  BEGIN 
	SELECT * FROM `products` WHERE `type` = product_type;
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `getUserById` (IN `id` INT)  BEGIN
	SELECT * FROM `users` where `user_id` = id;
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `getUserByUsername` (IN `name` VARCHAR(50))  BEGIN
	SELECT * FROM `users` where `username` = name;
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `getUsers` ()  BEGIN
	SELECT * FROM `users`;
END$$

DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `accounts`
--

CREATE TABLE `accounts` (
  `account_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `shipping_address` text,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `account_type` enum('User','Admin','Guest') NOT NULL DEFAULT 'User',
  `account_status` int(11) NOT NULL DEFAULT '0',
  `logged_in` int(11) NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `accounts`
--

INSERT INTO `accounts` (`account_id`, `user_id`, `shipping_address`, `created_at`, `account_type`, `account_status`, `logged_in`) VALUES
(1, 18, 'Bel Air, Los Angeles!', '2017-12-02 12:37:03', 'User', 0, 0),
(2, 11, 'Perth , New Jersey', '2017-09-22 10:07:50', 'User', 0, 0),
(3, 2, NULL, '2017-09-22 09:07:50', 'Admin', 0, 0),
(5, 13, 'Kiltoom, Athlone', '2017-11-08 16:13:48', 'User', 0, 0),
(6, 12, 'Angers, France', '2017-11-19 09:23:15', 'User', 0, 0),
(7, 1, 'Nevada, Las Vegas', '2017-11-10 20:34:47', 'User', 0, 0);

--
-- Triggers `accounts`
--
DELIMITER $$
CREATE TRIGGER `updateLogLoggedIN` BEFORE UPDATE ON `accounts` FOR EACH ROW IF NEW.logged_in <> OLD.logged_in THEN
    INSERT INTO `log`(`user_id` , `log_type` , `log_description`) 			VALUES(NEW.user_id , "Account" , concat(NEW.account_id , " has Logged In"));
END IF
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `updateLogShippingAddressChange` AFTER UPDATE ON `accounts` FOR EACH ROW IF NEW.shipping_address <> OLD.shipping_address THEN
    INSERT INTO `log`(`user_id` , `log_type` , `log_description`) 			VALUES(NEW.user_id , "Account ID : " , concat(NEW.account_id , " has changed \t\tshipping address"));
END IF
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `basket_items`
--

CREATE TABLE `basket_items` (
  `basket_items_id` int(11) NOT NULL,
  `basket_id` int(11) NOT NULL,
  `item_id` int(11) NOT NULL,
  `quantity` int(11) NOT NULL DEFAULT '1'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `basket_items`
--

INSERT INTO `basket_items` (`basket_items_id`, `basket_id`, `item_id`, `quantity`) VALUES
(1, 4, 6, 2),
(5, 2, 7, 1);

-- --------------------------------------------------------

--
-- Table structure for table `log`
--

CREATE TABLE `log` (
  `log_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `product_id` int(11) DEFAULT NULL,
  `order_id` int(11) DEFAULT NULL,
  `log_type` enum('Order','Account','Stock','') NOT NULL,
  `log_description` text NOT NULL,
  `log_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `log`
--

INSERT INTO `log` (`log_id`, `user_id`, `product_id`, `order_id`, `log_type`, `log_description`, `log_time`) VALUES
(4, 11, NULL, NULL, 'Account', 'random has logged in', '2017-10-21 15:53:58'),
(5, 11, NULL, NULL, 'Account', 'random has logged in', '2017-10-21 16:04:16'),
(6, 11, 1, NULL, 'Stock', 'Product Liked', '2017-10-21 16:05:56'),
(7, 11, 1, NULL, 'Stock', 'Product Added to Cart', '2017-10-21 16:08:25'),
(8, 11, NULL, NULL, 'Account', 'random has logged in', '2017-10-26 13:50:59'),
(9, 11, 1, NULL, 'Stock', 'Product Liked', '2017-10-26 13:56:44'),
(10, 11, NULL, NULL, 'Account', 'random has logged in', '2017-11-07 10:40:40'),
(11, 11, NULL, NULL, 'Account', 'random has logged in', '2017-11-07 10:42:45'),
(12, 11, NULL, NULL, 'Account', 'random has logged in', '2017-11-07 10:44:37'),
(13, 11, NULL, NULL, 'Account', 'random has logged in', '2017-11-09 14:54:37'),
(14, 11, 2, NULL, 'Stock', 'Product Added to Cart', '2017-11-09 14:55:33'),
(15, 11, 2, NULL, 'Stock', 'Product Added to Cart', '2017-11-09 14:56:11'),
(16, 11, NULL, NULL, 'Account', 'random has logged in', '2017-11-10 20:07:27'),
(17, 11, NULL, NULL, 'Account', 'random has logged in', '2017-11-11 13:11:31'),
(18, 11, 6, NULL, 'Stock', 'Product Liked', '2017-11-11 13:11:54'),
(19, 11, 6, NULL, 'Stock', 'Product Added to Cart', '2017-11-11 13:11:54'),
(20, 11, 7, NULL, 'Stock', 'Product Liked', '2017-11-11 13:11:58'),
(21, 11, 7, NULL, 'Stock', 'Product Added to Cart', '2017-11-11 13:11:59'),
(22, 11, NULL, 9, 'Order', 'Order Completed', '2017-11-11 13:33:00'),
(23, 11, NULL, NULL, 'Account', 'random has logged in', '2017-11-11 13:34:16'),
(24, 11, NULL, NULL, 'Account', 'random has logged in', '2017-11-11 14:36:06'),
(25, 11, NULL, NULL, 'Account', 'random has logged in', '2017-11-11 15:44:50'),
(26, 12, NULL, NULL, 'Account', 'Account Created', '2017-11-13 19:51:50'),
(27, 12, NULL, NULL, 'Account', 'testing has logged in', '2017-11-13 19:54:22'),
(28, 12, 6, NULL, 'Stock', 'Product Liked', '2017-11-13 19:54:44'),
(29, 12, 6, NULL, 'Stock', 'Product Added to Cart', '2017-11-13 19:54:45'),
(30, 12, NULL, 10, 'Order', 'Order Completed', '2017-11-13 20:08:33'),
(31, 13, NULL, NULL, 'Account', 'Account Created', '2017-11-17 19:53:31'),
(32, 13, NULL, NULL, 'Account', 'mcoyle has logged in', '2017-11-17 19:53:42'),
(33, 13, 6, NULL, 'Stock', 'Product Added to Cart', '2017-11-17 19:53:46'),
(34, 13, 6, NULL, 'Stock', 'Product Liked', '2017-11-17 19:53:48'),
(35, 14, NULL, NULL, 'Account', 'Account Created', '2017-11-17 19:57:37'),
(36, 14, NULL, NULL, 'Account', 'Account Created', '2017-11-17 19:57:37'),
(37, 13, NULL, NULL, 'Account', 'mcoylehas logged 		in', '2017-11-17 20:17:06'),
(38, 13, NULL, NULL, 'Account', 'mcoyle has logged 		in', '2017-11-17 20:22:15'),
(40, 11, NULL, NULL, 'Account', 'random has logged 		in', '2017-12-02 11:09:30'),
(41, 11, 3, NULL, 'Stock', 'Product Added to Cart', '2017-12-02 11:10:17'),
(42, 11, 7, NULL, 'Stock', 'Product Added to Cart', '2017-12-02 11:10:22'),
(43, 11, NULL, 11, 'Order', 'Order Completed', '2017-12-02 11:10:30'),
(44, 11, NULL, NULL, 'Account', 'random has logged 		in', '2017-12-02 11:11:26'),
(49, 18, NULL, NULL, 'Account', 'Account Created', '2017-12-02 12:37:03'),
(50, 18, NULL, NULL, 'Account', '1 has changed 		shipping address in', '2017-12-02 12:57:36'),
(51, 11, 3, NULL, 'Stock', 'Product Added to Cart', '2017-12-02 13:01:05'),
(52, 11, NULL, 12, 'Order', 'Order Completed', '2017-12-02 14:02:18'),
(53, 11, NULL, NULL, 'Account', '2 has Logged In', '2017-12-02 17:40:38'),
(54, 11, NULL, NULL, 'Account', '2 has Logged In', '2017-12-02 17:52:18'),
(56, 11, NULL, NULL, 'Account', '2 has Logged In', '2017-12-02 18:04:22'),
(57, 11, NULL, NULL, 'Account', '2 has Logged In', '2017-12-02 18:04:27'),
(59, 12, NULL, NULL, 'Account', '6 has Logged In', '2017-12-02 18:09:12'),
(60, 12, NULL, NULL, 'Account', '6 has Logged In', '2017-12-02 18:09:14'),
(63, 11, NULL, NULL, 'Account', '2 has Logged In', '2017-12-02 18:40:24'),
(64, 11, NULL, NULL, 'Account', '2 has Logged In', '2017-12-02 18:40:33'),
(66, 11, NULL, NULL, 'Account', '2 has Logged In', '2017-12-07 18:45:05'),
(67, 11, 7, NULL, 'Stock', 'Product Added to Cart', '2017-12-07 18:45:11'),
(68, 11, NULL, NULL, 'Account', '2 has Logged In', '2017-12-07 18:51:35');

-- --------------------------------------------------------

--
-- Table structure for table `orders`
--

CREATE TABLE `orders` (
  `order_id` int(11) NOT NULL,
  `order_total` int(11) NOT NULL,
  `order_date` datetime NOT NULL,
  `Shipping_address` text NOT NULL,
  `user_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `orders`
--

INSERT INTO `orders` (`order_id`, `order_total`, `order_date`, `Shipping_address`, `user_id`) VALUES
(6, 640, '2017-10-15 15:19:50', 'Bredagh,\r\nKiltoom,\r\nAthlone', 11),
(7, 330, '2017-10-19 21:26:12', 'Bredagh,\r\nKiltoom,\r\nAthlone', 11),
(9, 360, '2017-11-11 13:33:00', 'Bredagh,\r\nKiltoom,\r\nAthlone', 11),
(10, 120, '2017-11-13 20:08:33', 'Test Address,\r\nAthlone', 12),
(11, 420, '2017-12-02 11:10:30', 'Bredagh,\r\nKiltoom,\r\nAthlone', 11),
(12, 360, '2017-12-02 14:02:18', 'Perth , New Jersey', 11);

-- --------------------------------------------------------

--
-- Table structure for table `order_items`
--

CREATE TABLE `order_items` (
  `order_items_id` int(11) NOT NULL,
  `item_id` int(11) NOT NULL,
  `order_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `order_items`
--

INSERT INTO `order_items` (`order_items_id`, `item_id`, `order_id`) VALUES
(3, 2, 6),
(4, 10, 7),
(7, 6, 9),
(8, 7, 9),
(9, 6, 10),
(10, 3, 11),
(11, 7, 11),
(12, 3, 12);

-- --------------------------------------------------------

--
-- Table structure for table `order_stock_levels`
--

CREATE TABLE `order_stock_levels` (
  `stock_level_id` int(11) NOT NULL,
  `item_id` int(11) NOT NULL,
  `amount` int(11) NOT NULL,
  `stock_tolerance` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `order_stock_levels`
--

INSERT INTO `order_stock_levels` (`stock_level_id`, `item_id`, `amount`, `stock_tolerance`) VALUES
(1, 10, 2, 2),
(2, 1, 3, 2),
(3, 2, 1, 2),
(4, 4, 2, 3),
(5, 5, 4, 3),
(6, 7, 5, 3),
(7, 8, 4, 4),
(8, 9, 3, 3),
(9, 6, 3, 4),
(10, 3, 4, 5),
(11, 11, 2, 2);

-- --------------------------------------------------------

--
-- Table structure for table `products`
--

CREATE TABLE `products` (
  `product_id` int(11) NOT NULL,
  `name` varchar(60) NOT NULL,
  `description` text NOT NULL,
  `type` enum('Pocket Watch','Modern Watch','Classic Watch','Smart Watch') NOT NULL,
  `price` int(11) NOT NULL,
  `image` varchar(80) NOT NULL,
  `date_added` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `products`
--

INSERT INTO `products` (`product_id`, `name`, `description`, `type`, `price`, `image`, `date_added`) VALUES
(1, 'Test Product', 'This is a Test', 'Classic Watch', 325, 'test.png', '2017-10-09 23:26:25'),
(2, 'Test Product 2', 'Another Test', 'Modern Watch', 320, 'test.png', '2017-10-10 21:07:28'),
(3, 'Classic Watch V2', 'Another Classic Watch', 'Modern Watch', 180, 'Capture.PNG', '2017-10-16 14:18:47'),
(4, 'Modern Watch V2', 'Another Modern Watch', 'Pocket Watch', 125, 'modern-watch.jpg', '2017-10-16 14:40:11'),
(6, 'Another Classic Watch V4', 'Another Classic Watch', 'Classic Watch', 120, 'marek-prygiel-54468.jpg', '2017-10-16 14:45:01'),
(7, 'Test Smart Watch', 'This is a smart watch', 'Smart Watch', 240, 'jens-kreuter-85267.jpg', '2017-10-18 20:57:38'),
(10, 'Testing Quantity', 'This is a test for product quantity and order levels', 'Pocket Watch', 167, 'pocket-watch.jpg', '2017-10-19 20:44:13'),
(11, 'Rolex Yacht Master', ' Overpriced Luxurious Watch', 'Classic Watch', 22000, 'andrea-natali-447547.jpg', '2017-12-02 14:13:24');

-- --------------------------------------------------------

--
-- Table structure for table `product_likes`
--

CREATE TABLE `product_likes` (
  `like_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `date_liked` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `product_likes`
--

INSERT INTO `product_likes` (`like_id`, `product_id`, `user_id`, `date_liked`) VALUES
(9, 2, 11, '2017-10-14 20:07:55'),
(10, 2, 1, '2017-10-15 13:39:46'),
(12, 1, 1, '2017-10-15 13:41:01'),
(13, 1, 11, '2017-10-26 14:56:44'),
(14, 6, 11, '2017-11-11 13:11:54'),
(15, 7, 11, '2017-11-11 13:11:58'),
(16, 6, 12, '2017-11-13 19:54:44'),
(17, 6, 13, '2017-11-17 19:53:48'),
(19, 3, 11, '2017-12-02 13:01:05');

-- --------------------------------------------------------

--
-- Table structure for table `reviews`
--

CREATE TABLE `reviews` (
  `review_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `star_count` decimal(1,1) DEFAULT NULL,
  `description` text NOT NULL,
  `title` text NOT NULL,
  `datetime` datetime NOT NULL,
  `user_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `reviews`
--

INSERT INTO `reviews` (`review_id`, `product_id`, `star_count`, `description`, `title`, `datetime`, `user_id`) VALUES
(2, 1, NULL, 'This is a test review, just to see how reviewing will look for the product view. \r\nReviewing is being based off of the amazon review style.', 'A Classic Watch', '2017-10-19 15:36:17', 2),
(3, 2, NULL, 'This is a test review for a test product, this review is based off of the amazon review system. ', 'A Classic Watch', '2017-10-19 15:44:11', 11),
(4, 1, NULL, 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Duis volutpat augue faucibus felis euismod maximus. Curabitur ullamcorper neque vitae felis blandit, a lobortis libero ultrices. Sed tristique velit non erat tempor elementum. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus.', 'What a Watch', '2017-10-19 20:10:21', 11),
(5, 3, NULL, 'Not worth the price!', 'Average Watch', '2017-12-02 13:01:29', 11),
(6, 7, NULL, 'Similar to the samsung gear s3', 'Similar to an S3', '2017-12-07 18:50:14', 11);

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `user_id` int(11) NOT NULL,
  `first_name` varchar(30) NOT NULL,
  `last_name` varchar(30) NOT NULL,
  `email` varchar(60) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(80) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`user_id`, `first_name`, `last_name`, `email`, `username`, `password`) VALUES
(1, 'Mark', 'Coyle', 'markcoyle14@hotmail.com', 'markc456', '$5$rounds=535000$1lFDmOYHhs/5I/2W$36joloMO4m73h8MjCXKcYhU5cff5aCs1ax6LJjGJgE8'),
(2, 'Joe', 'Bloggs', 'jbloggs@gmail.com', 'jbloggs', '$5$rounds=535000$qQf95ch/enYde9Qw$0p1nGbKEZH.FB/zVPgAfkMyCyZVQglXvEIp5iIS5YU.'),
(11, 'Bon', 'Jovi', 'testaccount@testshop.com', 'random', '$5$rounds=535000$M2n7WxQ0q6FPCW8P$36euQTdusJeKwfcFguFmA0XaZp8bWgeQK9EGZstH.13'),
(12, 'Test', 'Order', 'tester@test.com', 'testing', '$5$rounds=535000$ubaPCud09blnQLbS$yQxHbzi1mnm8TSTmX.sAqyfSngDL3v2w5uaR1vkTcn7'),
(13, 'mark', 'coyle', 'markcoyle14@gmail.com', 'mcoyle', '$5$rounds=535000$sJr3mBXoeKrmdHt7$TSbc0c0QwXlHxlpuXqR8Zlw9QvYJC9EqwOl7bvrOWnD'),
(18, 'Will', 'Smith', 'wsmith@gmail.com', 'FreshPrince', '$5$rounds=535000$co9j4uuZ1IPL9Wlp$GDkHrBwrj1p.U.4FeOsmhw9s8Ehw2U5QHCZUxl9xci8');

--
-- Triggers `users`
--
DELIMITER $$
CREATE TRIGGER `createBasket` AFTER INSERT ON `users` FOR EACH ROW INSERT INTO `user_basket`(`user_id`) VALUES(NEW.user_id)
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `user_basket`
--

CREATE TABLE `user_basket` (
  `basket_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `user_basket`
--

INSERT INTO `user_basket` (`basket_id`, `user_id`) VALUES
(1, 1),
(2, 11),
(3, 12),
(4, 13),
(10, 18);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `accounts`
--
ALTER TABLE `accounts`
  ADD PRIMARY KEY (`account_id`);

--
-- Indexes for table `basket_items`
--
ALTER TABLE `basket_items`
  ADD PRIMARY KEY (`basket_items_id`);

--
-- Indexes for table `log`
--
ALTER TABLE `log`
  ADD PRIMARY KEY (`log_id`);

--
-- Indexes for table `orders`
--
ALTER TABLE `orders`
  ADD PRIMARY KEY (`order_id`);

--
-- Indexes for table `order_items`
--
ALTER TABLE `order_items`
  ADD PRIMARY KEY (`order_items_id`);

--
-- Indexes for table `order_stock_levels`
--
ALTER TABLE `order_stock_levels`
  ADD PRIMARY KEY (`stock_level_id`);

--
-- Indexes for table `products`
--
ALTER TABLE `products`
  ADD PRIMARY KEY (`product_id`);

--
-- Indexes for table `product_likes`
--
ALTER TABLE `product_likes`
  ADD PRIMARY KEY (`like_id`);

--
-- Indexes for table `reviews`
--
ALTER TABLE `reviews`
  ADD PRIMARY KEY (`review_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`user_id`);

--
-- Indexes for table `user_basket`
--
ALTER TABLE `user_basket`
  ADD PRIMARY KEY (`basket_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `accounts`
--
ALTER TABLE `accounts`
  MODIFY `account_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `basket_items`
--
ALTER TABLE `basket_items`
  MODIFY `basket_items_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `log`
--
ALTER TABLE `log`
  MODIFY `log_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=69;

--
-- AUTO_INCREMENT for table `orders`
--
ALTER TABLE `orders`
  MODIFY `order_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT for table `order_items`
--
ALTER TABLE `order_items`
  MODIFY `order_items_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT for table `order_stock_levels`
--
ALTER TABLE `order_stock_levels`
  MODIFY `stock_level_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT for table `products`
--
ALTER TABLE `products`
  MODIFY `product_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT for table `product_likes`
--
ALTER TABLE `product_likes`
  MODIFY `like_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=20;

--
-- AUTO_INCREMENT for table `reviews`
--
ALTER TABLE `reviews`
  MODIFY `review_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `user_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=19;

--
-- AUTO_INCREMENT for table `user_basket`
--
ALTER TABLE `user_basket`
  MODIFY `basket_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
