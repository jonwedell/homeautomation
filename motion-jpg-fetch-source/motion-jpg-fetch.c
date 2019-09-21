/* Jon Wedell's cmdline jpeg grabber for Motion: motion-jpg-fetch
 * This program is published under the GNU Public license
 *  Version 3, 29 June 2007
 *
 * Usage: motion-jpg-fetch motion_server_ipaddr motion_server_stream_port
 *
 * Adapted from:
 *
 * Kenneth Lavrsen's jpeg grabber for Motion: nph-mjgrab
 *  Published under the GNU Public license
 *  Version 1.0 - 2003 November 19
 *
 * Located at: http://www.lavrsen.dk/foswiki/bin/view/Motion/MjpegProxyGrab
 *
 *
 *
 *
 *
 *  The program opens a socket to a running Motion webcam server
 *  It then fetches ONE and only one frame of the mjpeg stream
 *  and sends it to standard out.
 *  It then closes the socket and terminates.
 *
 *  Program can be built with this command:
 *  gcc -Wall -O3 -o motion-jpg-fetch motion-jpg-fetch.c
 *
 *
 */

#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <stdio.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>

int main(int argc, char *argv[])
{
    int sockfd;
    FILE *fd;
    int len;
    struct sockaddr_in address;
    int result;
    int jpglength;
    int port;
    char garbage1[80] = "";
    char garbage2[30] = "";
    char * ip_addr = malloc(sizeof(char) * 16);

    // Check arguments
    if( argc != 3 ){
        printf("Usage: %s ipaddr port\n", argv[0]);
        exit(1);
    }

    // Get camera number and IP from cmdline
    sscanf(argv[1], "%s16", ip_addr);
    sscanf(argv[2], "%d", &port);

    // Create a socket for the client.
    sockfd = socket(AF_INET, SOCK_STREAM, 0);

    // Name the socket, as agreed with the server.
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = inet_addr(ip_addr);
    address.sin_port = htons(port);
    len = sizeof(address);

    // Now connect our socket to the server's socket.
    result = connect(sockfd, (struct sockaddr *)&address, len);

    if(result == -1){
        perror("Cannot connect to Motion");
        exit(1);
    }

    fd = fdopen(sockfd,"r");

    if(fd == NULL){
        perror("Cannot connect to Motion");
        exit(1);
    }

    // We can now read/write via sockfd.
    while(strncmp(garbage1, "Content-Length:", 15)!=0)
    {
        fgets(garbage1, 70, fd);
    }

    sscanf(garbage1, "%s%d", garbage2, &jpglength);
    fgets(garbage1, 70, fd);

    // Allocate room for one image in RAM based on image size
    char * chbuffer = malloc(jpglength);

    fread(chbuffer, 1, jpglength, fd);
    fwrite(chbuffer, 1, jpglength, stdout);
    fflush(stdout);

    fclose(fd);
    close(sockfd);

    // Free our allocations
    free(chbuffer);
    free(ip_addr);

    exit(0);
}
